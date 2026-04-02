import os
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # type: ignore
from tensorflow.keras.applications import MobileNetV2  # type: ignore
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout  # type: ignore
from tensorflow.keras.models import Model  # type: ignore
from tensorflow.keras.optimizers import Adam  # type: ignore
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json
import time
from datetime import datetime
from typing import cast, Any, List

load_dotenv()

# ==========================================
# 📂 CONFIGURAÇÃO DE DIRETÓRIOS E CAMINHOS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
MODULES_DIR = os.path.dirname(MODULE_DIR)
BACKEND_DIR = os.path.dirname(MODULES_DIR)

DATASET_DIR = os.path.join(MODULE_DIR, "datasets", "drishti_gs")
METADATA_FILE = os.path.join(DATASET_DIR, "Drishti-GS1_diagnosis.xlsx")
IMAGE_DIR = os.path.join(DATASET_DIR, "Training", "Images")

TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")
os.makedirs(TRAIN_RESULTS_DIR, exist_ok=True)

MODEL_SAVE_PATH = os.path.join(TRAIN_RESULTS_DIR, "glaucoma_cnn_model.h5")
INFO_SAVE_PATH = os.path.join(TRAIN_RESULTS_DIR, "glaucoma_info.json")

# ==========================================
# 🗄️ PARÂMETROS E BANCO
# ==========================================
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

user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")
db_name = os.getenv("POSTGRES_DB", "episcope")

DB_URL = f"postgresql://{user}:{password}@db:5432/{db_name}"
engine = create_engine(DB_URL)


def preprocess_image(
    image_path: str,
    target_size: tuple[int, int] = (TRAIN_PARAMS["img_size"], TRAIN_PARAMS["img_size"]),  # type: ignore
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


def load_data_from_excel(metadata_path: str, image_dir: str):
    print(f"Carregando metadados de: {metadata_path}")
    try:
        try:
            df = pd.read_excel(metadata_path)
        except ValueError:
            df = pd.read_csv(metadata_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {metadata_path}")

    filename_col = "Drishti-GS File"
    label_col = "Total"
    if filename_col not in df.columns or label_col not in df.columns:
        raise ValueError(f"Colunas '{filename_col}' ou '{label_col}' ausentes.")

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


def main():
    print("Iniciando script de treinamento da CNN (V3 - Com Logs)...")
    start_time = time.time()

    try:
        images, labels, class_names = load_data_from_excel(METADATA_FILE, IMAGE_DIR)

        label_encoder = LabelEncoder()
        label_encoder.fit(labels)
        encoded_labels = label_encoder.transform(labels)

        X_train, X_val, y_train, y_val = train_test_split(
            images,
            encoded_labels,
            test_size=float(TRAIN_PARAMS["test_split"]),
            random_state=42,
            stratify=encoded_labels,
        )

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

        b_size = int(TRAIN_PARAMS["batch_size"])
        train_generator = train_datagen.flow(X_train, y_train, batch_size=b_size)
        val_generator = val_datagen.flow(X_val, y_val, batch_size=b_size)

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

        optimizer = Adam(learning_rate=float(TRAIN_PARAMS["learning_rate"]))
        model.compile(
            optimizer=optimizer, loss="binary_crossentropy", metrics=["accuracy"]
        )

        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True
        )

        print("Iniciando Fase 1...")
        history = model.fit(
            train_generator,
            steps_per_epoch=max(1, len(X_train) // b_size),
            epochs=int(TRAIN_PARAMS["initial_epochs"]),
            validation_data=val_generator,
            validation_steps=max(1, len(X_val) // b_size),
            callbacks=[early_stopping],
        )

        print("Iniciando Fase 2 (Fine-Tuning)...")
        base_model.trainable = True
        for layer in base_model.layers[:100]:
            layer.trainable = False

        optimizer_fine_tune = Adam(learning_rate=float(TRAIN_PARAMS["fine_tune_lr"]))
        model.compile(
            optimizer=optimizer_fine_tune,
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        # 👇 Solução pro history.epoch
        initial_epoch_value = getattr(history, "epoch", [0])[-1]

        history_fine_tune = model.fit(
            train_generator,
            steps_per_epoch=max(1, len(X_train) // b_size),
            epochs=int(TRAIN_PARAMS["initial_epochs"])
            + int(TRAIN_PARAMS["fine_tune_epochs"]),
            initial_epoch=initial_epoch_value,
            validation_data=val_generator,
            validation_steps=max(1, len(X_val) // b_size),
            callbacks=[early_stopping],
        )

        print("Avaliando modelo final...")

        # 👇 Solução pro evaluate: Extraímos a lista manualmente
        eval_result = model.evaluate(val_generator, steps=max(1, len(X_val) // b_size))
        eval_list = cast(List[float], eval_result)
        accuracy = eval_list[1] if len(eval_list) > 1 else 0.0

        y_pred_prob = model.predict(X_val)
        y_pred_class = (y_pred_prob > 0.5).astype(int).flatten()

        report_dict = classification_report(
            y_val, y_pred_class, target_names=label_encoder.classes_, output_dict=True
        )

        model.save(MODEL_SAVE_PATH)

        model_info = {
            "image_size": TRAIN_PARAMS["img_size"],
            "class_names": label_encoder.classes_.tolist(),
        }
        with open(INFO_SAVE_PATH, "w") as f:
            json.dump(model_info, f)

        print("\nSalvando log de treinamento no banco de dados...")

        try:
            insert_query = text("""
                INSERT INTO model_training_logs 
                (model_name, version, parameters, feature_importance, metrics, accuracy, dataset_size, created_at)
                VALUES (:model_name, :version, :parameters, :feature_importance, :metrics, :accuracy, :dataset_size, :created_at)
            """)

            with engine.begin() as conn:
                conn.execute(
                    insert_query,
                    {
                        "model_name": "Glaucoma_CNN_Specialist",
                        "version": "v3_MobileNetV2_FineTuned_100",
                        "parameters": json.dumps(
                            {**TRAIN_PARAMS, "unfrozen_layers": 100}
                        ),
                        "feature_importance": "Deep-Features (GAP Layer)",
                        "metrics": json.dumps(report_dict),
                        "accuracy": float(accuracy),
                        "dataset_size": len(images),
                        "created_at": datetime.utcnow(),  # 👇 Solução do datetime
                    },
                )

            print("Log CNN salvo com sucesso!")
        except Exception as e:
            print(f"AVISO: Falha ao salvar log no banco: {e}")

        print(f"Concluído em {time.time() - start_time:.2f} s.")

    except Exception as e:
        print(f"Erro Fatal: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
