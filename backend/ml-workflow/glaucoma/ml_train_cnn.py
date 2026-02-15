import os
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json
import time

load_dotenv()

print("Iniciando script de treinamento da CNN (V3 - Com Logs)...")
start_time = time.time()


DATASET_DIR = "/app/backend/data/drishti_gs"
METADATA_FILE = os.path.join(DATASET_DIR, "Drishti-GS1_diagnosis.xlsx")
IMAGE_DIR = os.path.join(DATASET_DIR, "Training", "Images")

ARTIFACTS_DIR = "/app/backend/model_artifacts"
MODEL_SAVE_PATH = os.path.join(ARTIFACTS_DIR, "glaucoma_cnn_model.h5")
INFO_SAVE_PATH = os.path.join(ARTIFACTS_DIR, "glaucoma_info.json")


TRAIN_PARAMS = {
    "img_size": 224,
    "batch_size": 16,
    "initial_epochs": 20,
    "fine_tune_epochs": 20,
    "learning_rate": 0.001,
    "fine_tune_lr": 0.00001,
    "test_split": 0.2,
    "architecture": "MobileNetV2",
}


DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)


def preprocess_image(
    image_path, target_size=(TRAIN_PARAMS["img_size"], TRAIN_PARAMS["img_size"])
):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, target_size)
        img_normalized = img_resized / 255.0
        return img_normalized
    except Exception as e:
        print(f"Erro processando {image_path}: {e}")
        return None


def load_data_from_excel(metadata_path, image_dir):
    
    
    print(f"Carregando metadados de: {metadata_path}")
    try:
        try:
            df = pd.read_excel(metadata_path)
        except ValueError:
            df = pd.read_csv(metadata_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Arquivo de metadados não encontrado em {metadata_path}."
        )

    filename_col = "Drishti-GS File"
    label_col = "Total"
    if filename_col not in df.columns or label_col not in df.columns:
        raise ValueError(f"Colunas '{filename_col}' ou '{label_col}' não encontradas.")

    images = []
    labels = []
    class_names = sorted(df[label_col].unique().tolist())
    print(f"Classes encontradas: {class_names}")

    for index, row in df.iterrows():
        base_filename = str(row[filename_col]).strip().replace("'", "")
        img_filename = f"{base_filename}.png"
        img_path = os.path.join(image_dir, img_filename)

        if not os.path.exists(img_path):
            img_filename = f"{base_filename}.jpg"
            img_path = os.path.join(image_dir, img_filename)
            if not os.path.exists(img_path):
                continue

        processed_img = preprocess_image(img_path)
        if processed_img is not None:
            images.append(processed_img)
            labels.append(row[label_col])

    print(f"Total de imagens carregadas: {len(images)}")
    return np.array(images), np.array(labels), class_names


try:
    images, labels, class_names = load_data_from_excel(METADATA_FILE, IMAGE_DIR)

    label_encoder = LabelEncoder()
    label_encoder.fit(labels)
    encoded_labels = label_encoder.transform(labels)
    print(f"Labels codificados: {list(label_encoder.classes_)}")

    X_train, X_val, y_train, y_val = train_test_split(
        images,
        encoded_labels,
        test_size=TRAIN_PARAMS["test_split"],
        random_state=42,
        stratify=encoded_labels,
    )
    print(f"Treino: {len(X_train)}, Validação: {len(X_val)}")

    train_datagen = ImageDataGenerator(
        rotation_range=30,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        zoom_range=0.15,
        horizontal_flip=True,
        fill_mode="nearest",
    )
    val_datagen = ImageDataGenerator()
    train_generator = train_datagen.flow(
        X_train, y_train, batch_size=TRAIN_PARAMS["batch_size"]
    )
    val_generator = val_datagen.flow(
        X_val, y_val, batch_size=TRAIN_PARAMS["batch_size"]
    )

    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(TRAIN_PARAMS["img_size"], TRAIN_PARAMS["img_size"], 3),
    )
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation="sigmoid")(x)
    model = Model(inputs=base_model.input, outputs=predictions)

    optimizer = Adam(learning_rate=TRAIN_PARAMS["learning_rate"])
    model.compile(optimizer=optimizer, loss="binary_crossentropy", metrics=["accuracy"])

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=10, restore_best_weights=True
    )

    print("Iniciando Fase 1...")
    history = model.fit(
        train_generator,
        steps_per_epoch=max(1, len(X_train) // TRAIN_PARAMS["batch_size"]),
        epochs=TRAIN_PARAMS["initial_epochs"],
        validation_data=val_generator,
        validation_steps=max(1, len(X_val) // TRAIN_PARAMS["batch_size"]),
        callbacks=[early_stopping],
    )

    print("Iniciando Fase 2 (Fine-Tuning)...")
    base_model.trainable = True
    fine_tune_at = 100
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    optimizer_fine_tune = Adam(learning_rate=TRAIN_PARAMS["fine_tune_lr"])
    model.compile(
        optimizer=optimizer_fine_tune, loss="binary_crossentropy", metrics=["accuracy"]
    )

    history_fine_tune = model.fit(
        train_generator,
        steps_per_epoch=max(1, len(X_train) // TRAIN_PARAMS["batch_size"]),
        epochs=TRAIN_PARAMS["initial_epochs"] + TRAIN_PARAMS["fine_tune_epochs"],
        initial_epoch=history.epoch[-1],
        validation_data=val_generator,
        validation_steps=max(1, len(X_val) // TRAIN_PARAMS["batch_size"]),
        callbacks=[early_stopping],
    )

    print("Avaliando modelo final...")
    loss, accuracy = model.evaluate(
        val_generator, steps=max(1, len(X_val) // TRAIN_PARAMS["batch_size"])
    )

    y_pred_prob = model.predict(X_val)
    y_pred_class = (y_pred_prob > 0.5).astype(int).flatten()

    report_dict = classification_report(
        y_val, y_pred_class, target_names=label_encoder.classes_, output_dict=True
    )

    print("\n--- Relatório (CNN): ---")
    print(
        classification_report(y_val, y_pred_class, target_names=label_encoder.classes_)
    )

    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)
    model.save(MODEL_SAVE_PATH)

    model_info = {
        "image_size": TRAIN_PARAMS["img_size"],
        "class_names": label_encoder.classes_.tolist(),
    }
    with open(INFO_SAVE_PATH, "w") as f:
        json.dump(model_info, f)

    print("\nSalvando log de treinamento no banco de dados...")
    try:
        log_entry_orm = {
            "model_name": "Glaucoma_CNN",
            "version": "MobileNetV2_FT",
            "parameters": TRAIN_PARAMS,
            "feature_importance": None,
            "metrics": report_dict,
            "accuracy": accuracy,
            "dataset_size": len(images),
            "created_at": pd.Timestamp.utcnow(),
        }

        insert_query = text("""
            INSERT INTO model_training_logs 
            (model_name, version, parameters, feature_importance, metrics, accuracy, dataset_size, created_at)
            VALUES (:model_name, :version, :parameters, :feature_importance, :metrics, :accuracy, :dataset_size, :created_at)
        """)

        with engine.connect() as conn:
            conn.execute(
                insert_query,
                {
                    "model_name": log_entry_orm["model_name"],
                    "version": log_entry_orm["version"],
                    "parameters": json.dumps(log_entry_orm["parameters"]),
                    "feature_importance": None,
                    "metrics": json.dumps(log_entry_orm["metrics"]),
                    "accuracy": log_entry_orm["accuracy"],
                    "dataset_size": log_entry_orm["dataset_size"],
                    "created_at": log_entry_orm["created_at"],
                },
            )
            conn.commit()

        print("Log CNN salvo com sucesso!")

    except Exception as e:
        print(f"AVISO: Falha ao salvar log no banco: {e}")

    end_time = time.time()
    print(f"Concluído em {end_time - start_time:.2f} s.")

except Exception as e:
    print(f"Erro Fatal: {e}")
    import traceback

    traceback.print_exc()
