import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ==========================================
# 📂 CONFIGURAÇÃO DE DIRETÓRIOS E CAMINHOS
# ==========================================
# SCRIPT_DIR = backend/modules/chest_xray/ml-workflow
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# MODULE_DIR = backend/modules/chest_xray
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
# MODULES_DIR = backend/modules
MODULES_DIR = os.path.dirname(MODULE_DIR)
# BACKEND_DIR = backend
BACKEND_DIR = os.path.dirname(MODULES_DIR)

# Caminho para o Dataset
DATASET_DIR = os.path.join(BACKEND_DIR, "data", "chest_xray_dataset", "chest_xray")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")

# 🎯 NOVO REQUISITO: Pasta exclusiva para os resultados do modelo no próprio módulo
TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")
os.makedirs(TRAIN_RESULTS_DIR, exist_ok=True) # Garante que a pasta existe!

MODEL_SAVE_PATH = os.path.join(TRAIN_RESULTS_DIR, "xray_cnn.h5")

# ==========================================
# 🗄️ BANCO DE DADOS
# ==========================================
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

TRAIN_PARAMS = {
    "img_size": 224,
    "batch_size": 32,
    "epochs": 5,
    "optimizer": "adam",
    "loss": "binary_crossentropy",
    "architecture": "Custom_CNN_V1",
    "specialization": "Dropout_Regularized_Dense",
}

def build_and_train_model():
    print("🩻 Iniciando Pipeline de Treinamento de Raio-X...")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=(224, 224),
        batch_size=TRAIN_PARAMS["batch_size"],
        label_mode="binary",
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=(224, 224),
        batch_size=TRAIN_PARAMS["batch_size"],
        label_mode="binary",
    )

    class_names = train_ds.class_names
    print(f"🧬 Classes detectadas: {class_names}")

    model = models.Sequential(
        [
            layers.Rescaling(1.0 / 255, input_shape=(224, 224, 3)),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer=TRAIN_PARAMS["optimizer"],
        loss=TRAIN_PARAMS["loss"],
        metrics=["accuracy"],
    )

    print("\n🚀 Iniciando o Treinamento...")
    history = model.fit(train_ds, validation_data=val_ds, epochs=TRAIN_PARAMS["epochs"])

    final_accuracy = history.history["val_accuracy"][-1]

    # Salvando no novo diretório 'train_results'
    model.save(MODEL_SAVE_PATH)
    print(f"\n✅ Modelo salvo com sucesso em: {MODEL_SAVE_PATH}")

    print("Salvando log no banco de dados para contexto do Agente...")
    try:
        log_entry = {
            "model_name": "XRay_CNN_Specialist",
            "version": "v1_Custom_Dropout",
            "parameters": json.dumps(
                {
                    **TRAIN_PARAMS,
                    "data_source": "Chest X-Ray Dataset (Pneumonia/Normal)",
                    "class_mapping": class_names,
                }
            ),
            "feature_importance": "CNN_Activation_Maps",
            "metrics": json.dumps(
                {
                    "final_val_accuracy": float(final_accuracy),
                    "history": {
                        k: [float(x) for x in v] for k, v in history.history.items()
                    },
                }
            ),
            "accuracy": float(final_accuracy),
            "dataset_size": tf.data.experimental.cardinality(train_ds).numpy()
            * TRAIN_PARAMS["batch_size"],
            "created_at": datetime.now(),
        }

        insert_query = text("""
            INSERT INTO model_training_logs 
            (model_name, version, parameters, feature_importance, metrics, accuracy, dataset_size, created_at)
            VALUES (:model_name, :version, :parameters, :feature_importance, :metrics, :accuracy, :dataset_size, :created_at)
        """)

        with engine.connect() as conn:
            conn.execute(insert_query, log_entry)
            conn.commit()
        print("Log X-Ray salvo com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao salvar log: {e}")

if __name__ == "__main__":
    build_and_train_model()