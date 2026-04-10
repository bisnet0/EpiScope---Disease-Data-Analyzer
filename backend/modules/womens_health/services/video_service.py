import cv2
import os
import numpy as np
from deepface import DeepFace  # type: ignore
import mediapipe as mp # type: ignore

# Inicializamos o Mediapipe Face Detection (mais leve que DeepFace para busca inicial)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

def process_womens_video(video_path: str):
    """
    Analisa microexpressões faciais usando Mediapipe para detecção e DeepFace para emoção.
    """
    print(f"🎬 [VIDEO SERVICE]: Analisando frames de {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    emotions_history = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Analisamos 1 frame a cada 15 para performance extrema no container
        if frame_count % 15 == 0:
            # Converte para RGB (Mediapipe espera RGB, OpenCV lê BGR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame_rgb)

            # Só chama o DeepFace se o Mediapipe confirmar que TEM um rosto
            if results.detections:
                try:
                    # DeepFace analyze
                    analysis = DeepFace.analyze(
                        frame, 
                        actions=['emotion'], 
                        enforce_detection=False,
                        detector_backend='skip' # Já detectamos com Mediapipe, pula a detecção interna
                    )
                    dominant_emotion = analysis[0]['dominant_emotion']
                    emotions_history.append(dominant_emotion)
                except Exception as e:
                    print(f"⚠️ Erro ao analisar frame {frame_count}: {e}")
                    continue
        
        frame_count += 1
    
    cap.release()

    if not emotions_history:
        return {"status": "error", "message": "Nenhuma face detectada no vídeo"}

    from collections import Counter
    emotion_counts = Counter(emotions_history)
    total = len(emotions_history)
    
    # Criamos o sumário com tipos explícitos para evitar erro do Pylance
    summary = {str(emotion): float(count / total) for emotion, count in emotion_counts.items()}
    
    # CORREÇÃO DO ERRO 'max': Usamos uma função lambda explícita
    # Isso diz ao Python: "Pegue a chave x e compare pelo valor summary[x]"
    dominant = max(summary, key=lambda x: summary[x])
    
    has_incongruence = summary.get('happy', 0.0) > 0.2
    
    return {
        "dominant_emotion": dominant,
        "emotion_distribution": summary,
        "clinical_alerts": ["⚠️ Possível incongruência afetiva detectada"] if has_incongruence else [],
        "total_frames_analyzed": len(emotions_history)
    }