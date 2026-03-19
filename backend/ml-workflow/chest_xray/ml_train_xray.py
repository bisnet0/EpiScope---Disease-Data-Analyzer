import os
import tensorflow as tf
from tensorflow.keras import layers, models

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATASET_DIR = os.path.join(BACKEND_DIR, "data", "chest_xray_dataset", "chest_xray")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
MODEL_SAVE_PATH = os.path.join(SCRIPT_DIR, "xray_cnn.h5")


def build_and_train_model():
    print("🩻 Iniciando Pipeline de Treinamento de Raio-X...")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR, image_size=(224, 224), batch_size=32, label_mode="binary"
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR, image_size=(224, 224), batch_size=32, label_mode="binary"
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

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    print("\n🚀 Iniciando o Treinamento (Pode demorar dependendo da sua CPU/GPU)...")

    history = model.fit(train_ds, validation_data=val_ds, epochs=5)

    model.save(MODEL_SAVE_PATH)
    print(f"\n✅ Treinamento concluído! Modelo salvo em: {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    build_and_train_model()
