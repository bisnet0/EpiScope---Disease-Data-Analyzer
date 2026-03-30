import os
import hashlib
import tensorflow as tf

# 👇 Imports ajustados para a nova arquitetura
from backend.modules.auth.models.user_model import db
from backend.modules.chest_xray.models.xray_model import XRayDiagnosis

# ==========================================
# 📂 RESOLUÇÃO DINÂMICA DE CAMINHOS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")
MODEL_PATH = os.path.join(TRAIN_RESULTS_DIR, "xray_cnn.h5")

# Inicialização do modelo CNN de Raio-X
xray_model = None
if os.path.exists(MODEL_PATH):
    try:
        xray_model = tf.keras.models.load_model(MODEL_PATH)
        print("[X-RAY SERVICE] 🩻 Modelo CNN de Raio-X carregado com sucesso!")
    except Exception as e:
        print(f"⚠️ [X-RAY SERVICE] Erro ao carregar modelo: {e}")
else:
    print(f"⚠️ [X-RAY SERVICE] Modelo não encontrado em {MODEL_PATH}. Treine o modelo primeiro.")


def run_xray_pipeline(image_bytes: bytes, user_id: str):
    if xray_model is None:
        return {
            "error": "Modelo de IA não treinado. Execute o script de treinamento primeiro."
        }, 500

    print(f"[X-RAY SERVICE] 🩻 Processando imagem de Raio-X ({len(image_bytes)} bytes)...")
    img_hash = hashlib.sha256(image_bytes).hexdigest()

    try:
        # 1. REMOVEMOS O PIL! Usamos o motor nativo do TensorFlow para ler a imagem
        img = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)

        # 2. Redimensiona usando o mesmo algoritmo bilinear do treinamento
        img = tf.image.resize(img, [224, 224])

        # 3. Expande a dimensão para criar o lote (Batch = 1)
        img_tensor = tf.expand_dims(img, axis=0)
    except Exception as e:
        print(f"[X-RAY ERROR] Falha no decodificador do TF: {e}")
        return {"error": "Arquivo de imagem inválido."}, 400

    # Extrai a predição crua
    prediction_score = xray_model.predict(img_tensor)[0][0]

    prob_pneumonia = float(prediction_score)
    prob_normal = 1.0 - prob_pneumonia

    # 4. Régua de corte agressiva (0.85) para combater o viés do Kaggle
    if prob_pneumonia > 0.85:
        final_prediction = "Pneumonia"
        clinical_notes = "Sinais de consolidação pulmonar identificados pela rede neural. Sugestivo de Pneumonia."
    else:
        final_prediction = "Normal"
        clinical_notes = (
            "Campos pulmonares transparentes. Padrão radiológico dentro da normalidade."
        )

    probabilities = {
        "Normal": round(prob_normal, 4),
        "Pneumonia": round(prob_pneumonia, 4),
    }

    if user_id != "agent_request":
        try:
            new_diagnosis = XRayDiagnosis(
                user_id=user_id,
                image_hash=img_hash,
                prediction_result=final_prediction,
                probabilities=probabilities,
            )
            db.session.add(new_diagnosis)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[DB ERROR] Erro ao salvar Raio-X: {e}")

    result = {
        "success": True,
        "prediction": final_prediction,
        "analysis_details": {
            "model_used": "CNN_XRay_Keras_V1",
            "probabilities": probabilities,
            "clinical_notes": clinical_notes,
            "image_hash": img_hash,
        },
    }

    return result, 200