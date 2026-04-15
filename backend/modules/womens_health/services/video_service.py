import cv2
import os
import numpy as np
from deepface import DeepFace  # type: ignore

def process_womens_video(video_path: str):
    """
    Analisa microexpressões faciais usando o detector nativo do DeepFace.
    Detector 'opencv' é leve e resolve o problema do Mediapipe no Docker.
    """
    print(f"🎬 [VIDEO SERVICE]: Analisando frames de {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    emotions_history = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Analisamos 1 frame a cada 20 para compensar a falta do Mediapipe
        if frame_count % 20 == 0:
            try:
                # Usamos o detector 'opencv' que já vem no pacote
                analysis = DeepFace.analyze(
                    frame, 
                    actions=['emotion'], 
                    enforce_detection=False,
                    detector_backend='opencv' # <- Mudamos para OpenCV puro
                )
                dominant_emotion = analysis[0]['dominant_emotion']
                emotions_history.append(dominant_emotion)
            except Exception as e:
                # Se não detectar rosto nesse frame, apenas pula
                continue
        
        frame_count += 1
    
    cap.release()

    if not emotions_history:
        return {"status": "error", "message": "Nenhuma face detectada no vídeo"}

    from collections import Counter
    emotion_counts = Counter(emotions_history)
    total = len(emotions_history)
    
    summary = {str(emotion): float(count / total) for emotion, count in emotion_counts.items()}
    
    # Lambda para evitar erro de tipagem no max()
    dominant = max(summary, key=lambda x: summary[x])
    
    has_incongruence = summary.get('happy', 0.0) > 0.2
    summary = {str(emotion): float(count / total) for emotion, count in emotion_counts.items()}
    blend = interpret_emotional_blend(summary)
    
    return {
        "dominant_emotion": dominant,
        "emotional_blend": blend,
        "emotion_distribution": summary,
        "clinical_alerts": ["⚠️ Possível incongruência afetiva detectada"] if has_incongruence else [],
        "total_frames_analyzed": len(emotions_history)
    }
def interpret_emotional_blend(spectrum: dict):
    """
    Lógica de negócio para identificar misturas de sentimentos.
    """
    sad = spectrum.get('sad', 0)
    fear = spectrum.get('fear', 0)
    angry = spectrum.get('angry', 0)
    happy = spectrum.get('happy', 0)

    if sad > 0.3 and fear > 0.3:
        return "ANGÚSTIA_VULNERÁVEL"
    if sad > 0.3 and angry > 0.3:
        return "MELANCOLIA_REATIVA"
    if happy > 0.2 and (sad > 0.2 or fear > 0.2):
        return "AFETO_INCONGRUENTE" # O perigoso "rir para não chorar"
        
    return "PADRÃO_SIMPLES"