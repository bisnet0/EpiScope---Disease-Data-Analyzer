import os
from flask import request, jsonify

# 👇 Mantido o import do serviço (ajustaremos isso depois)
from backend.modules.core_agent.services.predict_service import predict_and_audit_service

def handle_prediction_request():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    model_type = request.form.get("type", "xray") # glaucoma ou xray
    
    # Garante que a pasta temporária existe antes de salvar
    temp_dir = os.path.join(os.getcwd(), "backend", "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Salva temporariamente
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        # Chama o serviço que faz TUDO (Predição + Auditoria + Registro)
        full_result = predict_and_audit_service(temp_path, model_type)
        
        return jsonify(full_result), 200
    finally:
        # Limpeza obrigatória do servidor
        if os.path.exists(temp_path):
            os.remove(temp_path)