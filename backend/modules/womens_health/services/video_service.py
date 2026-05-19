import os
import cv2
import joblib
import numpy as np
from deepface import DeepFace  # type: ignore
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "video_coercion_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "models", "video_scaler.pkl")

_video_model = None
_video_scaler = None


def load_video_ml_models():
    """Carrega a SVM treinada para detectar coação via microexpressões."""
    global _video_model, _video_scaler
    if _video_model is None and os.path.exists(MODEL_PATH):
        try:
            _video_model = joblib.load(MODEL_PATH)
            _video_scaler = joblib.load(SCALER_PATH)
            print("✅ [VIDEO SERVICE] Modelo SVM de Vídeo carregado com sucesso!")
        except Exception as e:
            print(f"⚠️ [VIDEO SERVICE] Erro ao carregar modelo ML: {e}")


def process_womens_video(video_path: str):
    """
    Analisa microexpressões faciais extraindo a média do espectro emocional
    e submetendo à Máquina de Vetores de Suporte (SVM).
    """
    load_video_ml_models()
    print(f"🎬 [VIDEO SERVICE]: Analisando frames de {video_path}")

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        return {"status": "error", "message": "Vídeo inválido ou vazio"}

    # Pega os 3 frames-chave (Exatamente como o script de treinamento)
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
                # 👇 A vacina para o Pylance: Tipamos como Any
                analysis: Any = DeepFace.analyze(
                    frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    detector_backend="opencv",
                    silent=True,
                )

                # Tratamento seguro se o retorno for lista ou dicionário
                if isinstance(analysis, list) and len(analysis) > 0:
                    face_data = analysis[0]
                elif isinstance(analysis, dict):
                    face_data = analysis
                else:
                    continue

                if isinstance(face_data, dict) and "emotion" in face_data:
                    emotion_dict = face_data["emotion"]
                    for emo in emotions_accumulated.keys():
                        emotions_accumulated[emo] += emotion_dict.get(emo, 0)
                    frames_processed += 1
            except Exception:
                # Se der erro de OpenCV/DeepFace no frame, segue a vida
                pass

    cap.release()

    if frames_processed == 0:
        return {"status": "error", "message": "Nenhuma face detectada no vídeo"}

    # Calcula a média real das emoções em % (0 a 100)
    avg_emotions = {
        k: float(v / frames_processed) for k, v in emotions_accumulated.items()
    }

    # 1. Heurísticas base (O que a API já fazia)
    dominant_emotion = max(avg_emotions, key=lambda x: avg_emotions[x])
    blend = interpret_emotional_blend(avg_emotions)

    clinical_alerts = []

    # Alerta Heurístico de Incongruência
    if avg_emotions.get("happy", 0.0) > 20.0 and (
        avg_emotions.get("sad", 0.0) > 20.0 or avg_emotions.get("fear", 0.0) > 20.0
    ):
        clinical_alerts.append(
            "⚠️ HEURÍSTICA: Possível incongruência afetiva detectada (Riso Nervoso)"
        )

    # 2. INFERÊNCIA DO MACHINE LEARNING (SVM)
    if _video_model and _video_scaler:
        # Prepara o vetor EXATAMENTE na ordem que o modelo foi treinado
        feature_vector = np.array(
            [
                avg_emotions["angry"],
                avg_emotions["disgust"],
                avg_emotions["fear"],
                avg_emotions["happy"],
                avg_emotions["sad"],
                avg_emotions["surprise"],
                avg_emotions["neutral"],
            ]
        ).reshape(1, -1)

        features_scaled = _video_scaler.transform(feature_vector)
        prediction = _video_model.predict(features_scaled)[0]
        prob = _video_model.predict_proba(features_scaled)[0][
            1
        ]  # Chance de ser Coação (Label 1)

        if prediction == 1 or prob > 0.60:
            clinical_alerts.append(
                f"🚨 ALERTA ML: Padrão facial de Coação/Risco identificado (Confiança: {prob * 100:.1f}%)"
            )

    frontend_distribution = {k: v / 100.0 for k, v in avg_emotions.items()}

    return {
        "status": "success",
        "dominant_emotion": dominant_emotion,
        "emotional_blend": blend,
        "emotion_distribution": frontend_distribution,
        "clinical_alerts": clinical_alerts,
        "total_frames_analyzed": frames_processed,
    }


def interpret_emotional_blend(spectrum: dict):
    """
    Lógica de negócio adaptada para usar o range 0-100 do DeepFace,
    identificando misturas de sentimentos perigosas.
    """
    sad = spectrum.get("sad", 0)
    fear = spectrum.get("fear", 0)
    angry = spectrum.get("angry", 0)
    happy = spectrum.get("happy", 0)

    # Valores adaptados para escala % do ML
    if sad > 30 and fear > 30:
        return "ANGÚSTIA_VULNERÁVEL"
    if sad > 30 and angry > 30:
        return "MELANCOLIA_REATIVA"
    if happy > 20 and (sad > 20 or fear > 20):
        return "AFETO_INCONGRUENTE"  # O perigoso "rir para não chorar"

    return "PADRÃO_SIMPLES"
