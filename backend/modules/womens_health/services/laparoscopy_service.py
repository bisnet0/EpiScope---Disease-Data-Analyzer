import os
import cv2
from ultralytics import YOLO # type: ignore
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Onde o seu modelo YOLOv8 treinado vai ficar salvo futuramente
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "yolo_laparoscopy.pt")

def load_yolo_model():
    """Carrega o modelo YOLOv8. Retorna None se ainda não estiver treinado."""
    if os.path.exists(YOLO_MODEL_PATH):
        try:
            model = YOLO(YOLO_MODEL_PATH)
            print("✅ [LAPAROSCOPIA] Modelo YOLOv8 Cirúrgico carregado!")
            return model
        except Exception as e:
            print(f"⚠️ Erro ao carregar YOLOv8: {e}")
            return None
    return None

def process_laparoscopy_video(video_path: str):
    """
    Processa vídeos de cirurgias ginecológicas (Histerectomia Laparoscópica).
    Busca por instrumentos cirúrgicos e sinais de complicações/sangramento.
    """
    print(f"🏥 [LAPAROSCOPIA]: Analisando cirurgia em {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    if total_frames <= 0:
        cap.release()
        return {"status": "error", "message": "Vídeo cirúrgico inválido"}

    model = load_yolo_model()
    
    detections_history = []
    frames_processed = 0
    bleeding_frames = 0
    
    # Vamos processar 1 frame a cada segundo de vídeo para não fritar a CPU
    frame_step = max(1, fps) 
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        if current_frame % frame_step == 0:
            if model:
                # INFERÊNCIA YOLOv8 REAL
                results = model(frame, verbose=False)
                # Extrai os nomes das classes detectadas no frame (ex: 'tool', 'bleeding')
                for r in results:
                    for box in r.boxes:
                        class_name = model.names[int(box.cls)]
                        detections_history.append(class_name)
                        if class_name == "bleeding":
                            bleeding_frames += 1
            else:
                # FALLBACK MOCK (Para você testar o endpoint do Front enquanto treina o YOLO)
                # Simula a detecção de instrumentos para não travar o desenvolvimento
                detections_history.extend(["grasper", "hook", "scissor"])
                if frames_processed > 5: # Simula sangramento no meio do vídeo
                    bleeding_frames += 1
                    detections_history.append("bleeding")
            
            frames_processed += 1

    cap.release()

    if frames_processed == 0:
        return {"status": "error", "message": "Nenhum frame processado."}

    # Análise Estatística da Cirurgia
    detection_counts = Counter(detections_history)
    
    clinical_alerts = []
    
    # Regra 1: Sangramento Anômalo (Se detectou sangramento em mais de 20% do tempo)
    bleeding_ratio = bleeding_frames / frames_processed if frames_processed > 0 else 0
    if bleeding_ratio > 0.20:
        clinical_alerts.append(f"🚨 ALERTA YOLO: Sangramento anômalo ou persistente detectado ({bleeding_ratio*100:.1f}% do tempo avaliado).")

    # Regra 2: Ausência de instrumentos (Câmera perdida ou oclusão de visão)
    if not any(tool in detection_counts for tool in ["grasper", "hook", "scissor", "tool"]):
         clinical_alerts.append("⚠️ AVISO YOLO: Perda de campo de visão ou ausência de instrumentos ativos.")

    return {
        "status": "success",
        "surgery_type": "Histerectomia Laparoscópica",
        "total_analyzed_seconds": frames_processed,
        "items_detected": dict(detection_counts),
        "bleeding_ratio": round(bleeding_ratio, 2),
        "clinical_alerts": clinical_alerts,
        "maestro_recommendation": "Acionar revisão médica. Possível complicação hemostática." if clinical_alerts else "Procedimento dentro da normalidade."
    }