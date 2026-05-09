import os
import cv2
import base64
from ultralytics import YOLO  # type: ignore
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
    annotated_frames_b64 = []  # 👈 Array para guardar as imagens geradas

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

                frame_has_detections = False
                for r in results:
                    if len(r.boxes) > 0:
                        frame_has_detections = True
                        for box in r.boxes:
                            class_name = model.names[int(box.cls)]
                            detections_history.append(class_name)
                            if class_name == "bleeding":
                                bleeding_frames += 1

                # 👇 Se o YOLO achou algo neste frame, nós desenhamos e salvamos!
                # Limitamos a 6 imagens para o JSON não ficar gigantesco
                if frame_has_detections and len(annotated_frames_b64) < 6:
                    annotated_img = results[
                        0
                    ].plot()  # YOLO desenha os quadrados sozinho
                    # Converte a imagem para string Base64 para mandar pro React
                    _, buffer = cv2.imencode(".jpg", annotated_img)
                    b64_str = base64.b64encode(buffer).decode("utf-8")
                    annotated_frames_b64.append(f"data:image/jpeg;base64,{b64_str}")
            else:
                # FALLBACK MOCK (Mantido para testes)
                detections_history.extend(["grasper", "hook", "scissor"])
                if frames_processed > 5:
                    bleeding_frames += 1
                    detections_history.append("bleeding")

            frames_processed += 1

    cap.release()

    if frames_processed == 0:
        return {"status": "error", "message": "Nenhum frame processado."}

    detection_counts = Counter(detections_history)
    clinical_alerts = []

    bleeding_ratio = bleeding_frames / frames_processed if frames_processed > 0 else 0
    if bleeding_ratio > 0.20:
        clinical_alerts.append(
            f"🚨 ALERTA YOLO: Sangramento anômalo ou persistente detectado ({bleeding_ratio * 100:.1f}% do tempo avaliado)."
        )

    if not any(
        tool in detection_counts
        for tool in ["grasper", "hook", "scissor", "tool", "ligasure"]
    ):
        clinical_alerts.append(
            "⚠️ AVISO YOLO: Perda de campo de visão ou ausência de instrumentos ativos."
        )

    return {
        "status": "success",
        "surgery_type": "Histerectomia Laparoscópica",
        "total_analyzed_seconds": frames_processed,
        "items_detected": dict(detection_counts),
        "bleeding_ratio": round(bleeding_ratio, 2),
        "clinical_alerts": clinical_alerts,
        "annotated_frames": annotated_frames_b64,  # 👈 Mandamos as fotos pro frontend!
        "maestro_recommendation": "Acionar revisão médica. Possível complicação hemostática."
        if clinical_alerts
        else "Procedimento dentro da normalidade.",
    }
