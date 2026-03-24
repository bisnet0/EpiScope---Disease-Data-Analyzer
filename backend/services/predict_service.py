import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from backend.agents.hospital_workflow import app as hospital_workflow_app

MODEL_PATHS = {
    "glaucoma": "backend/model_artifacts/glaucoma_cnn_model.h5", 
    "xray": "backend/ml-workflow/chest_xray/xray_cnn.h5", 
}

def load_and_predict(image_path, model_type):
    """Realiza a inferência básica da CNN"""
    model = tf.keras.models.load_model(MODEL_PATHS[model_type])
    
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    
    # Lógica simples de label (ajuste conforme suas classes)
    if model_type == "xray":
        label = "Pneumonia" if prediction[0][0] > 0.5 else "Normal"
    else:
        label = "Glaucomatous" if prediction[0][0] > 0.5 else "Normal"
        
    confidence = float(prediction[0][0] if label in ["Pneumonia", "Glaucomatous"] else 1 - prediction[0][0])
    
    return label, round(confidence * 100, 2)

def predict_and_audit_service(image_path, model_type):
    """
    O 'Pulo do Gato': Une a predição técnica com a decisão clínica
    """
    print(f"🔍 [PREDICT SERVICE]: Iniciando análise de {model_type}...")
    
    # 1. Inferência da CNN
    label, confidence = load_and_predict(image_path, model_type)
    diagnosis_text = f"{label} detectado em exame de {model_type} com {confidence}% de confiança."

    # 2. Orquestração com LangGraph (IA Tunada + Blockchain + SQL)
    print(f"🚀 [WORKFLOW]: Disparando auditoria para: {diagnosis_text}")
    
    # O .invoke roda todo o grafo que montamos
    workflow_result = hospital_workflow_app.invoke({"diagnosis": diagnosis_text})
    
    # Retorna o combo completo para o Controller
    return {
        "label": label,
        "confidence": confidence,
        "audit": workflow_result
    }