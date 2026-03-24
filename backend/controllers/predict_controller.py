from flask import request, jsonify
from backend.services.predict_service import predict_and_audit_service
import os

def handle_prediction_request():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    model_type = request.form.get("type", "xray") # glaucoma ou xray
    
    # Salva temporariamente
    temp_path = os.path.join("backend/data/temp", file.filename)
    file.save(temp_path)

    try:
        # Chama o serviço que faz TUDO (Predição + Auditoria + Registro)
        full_result = predict_and_audit_service(temp_path, model_type)
        
        return jsonify(full_result), 200
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)