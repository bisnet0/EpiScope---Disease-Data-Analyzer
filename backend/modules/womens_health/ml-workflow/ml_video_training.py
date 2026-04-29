import os
import gc
import cv2
import pandas as pd
import numpy as np
import joblib
from deepface import DeepFace  # type: ignore
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from typing import Any  # 👈 Adicione isso aqui!

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "datasets", "video")
CSV_FEATURES_PATH = os.path.join(BASE_DIR, "..", "datasets", "video_features.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "models", "video_coercion_model.pkl")
SCALER_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "models", "video_scaler.pkl")

EMOTION_MAP = {
    "ANG": 1,
    "DIS": 1,
    "FEA": 1,
    "SAD": 1,  # Risco
    "HAP": 0,
    "NEU": 0,  # Estável
}


def extract_video_features(file_path):
    cap = cv2.VideoCapture(file_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        return None

    # Pega apenas 3 frames do vídeo para não fritar a RAM
    target_frames = [
        int(total_frames * 0.25),
        int(total_frames * 0.5),
        int(total_frames * 0.75),
    ]
    emotions_accumulated = {
        "angry": 0,
        "disgust": 0,
        "fear": 0,
        "happy": 0,
        "sad": 0,
        "surprise": 0,
        "neutral": 0,
    }
    frames_processed = 0

    for f_idx in target_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if ret:
            try:
                # 👇 Tipamos como Any para o Pylance parar de tentar adivinhar
                res: Any = DeepFace.analyze(
                    frame, actions=["emotion"], enforce_detection=False, silent=True
                )

                if isinstance(res, list) and len(res) > 0:
                    face_data = res[0]
                elif isinstance(res, dict):
                    face_data = res
                else:
                    continue

                if isinstance(face_data, dict) and "emotion" in face_data:
                    emotion_dict = face_data["emotion"]

                    for emo in emotions_accumulated.keys():
                        emotions_accumulated[emo] += emotion_dict.get(emo, 0)
                    frames_processed += 1

            except Exception as e:
                pass

    cap.release()

    if frames_processed == 0:
        return None

    # Tira a média
    avg_emotions = [
        emotions_accumulated[k] / frames_processed for k in emotions_accumulated.keys()
    ]
    return avg_emotions


def build_incremental_dataset():
    if os.path.exists(CSV_FEATURES_PATH):
        print("✅ CSV de vídeo já existe. Indo direto para o treino!")
        return True

    print("⏳ Iniciando extração de vídeo. Isso vai demorar (pegue um café ☕)...")
    files = [
        f for f in os.listdir(DATASET_PATH) if f.endswith((".mp4", ".flv", ".avi"))
    ]
    total = len(files)

    with open(CSV_FEATURES_PATH, "w") as f:
        cols = [
            "angry",
            "disgust",
            "fear",
            "happy",
            "sad",
            "surprise",
            "neutral",
            "label",
        ]
        f.write(",".join(cols) + "\n")

        for idx, filename in enumerate(files):
            parts = filename.split("_")
            if len(parts) < 3:
                continue

            label = EMOTION_MAP.get(parts[2])
            if label is None:
                continue

            file_path = os.path.join(DATASET_PATH, filename)
            features = extract_video_features(file_path)

            if features is not None:
                row = np.append(features, label)
                f.write(",".join(map(str, row)) + "\n")

            if (idx + 1) % 50 == 0:
                print(f"Progresso Vídeo: {idx + 1}/{total} processados...")
                gc.collect()


def train_model():
    build_incremental_dataset()

    print("🧠 Treinando Máquina de Vetores de Suporte (SVM) para Expressões...")
    df = pd.read_csv(CSV_FEATURES_PATH)
    X = df.drop(columns=["label"])
    y = df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # SVM é excelente para cruzar fronteiras de emoções (ex: distinguir Tristeza de Neutro)
    model = SVC(kernel="rbf", probability=True, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\n📊 Relatório de Vídeo:")
    print(classification_report(y_test, y_pred, target_names=["Estável", "Coação"]))

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)
    joblib.dump(scaler, SCALER_OUTPUT_PATH)
    print("✅ Modelo SVM de vídeo salvo!")


if __name__ == "__main__":
    train_model()
