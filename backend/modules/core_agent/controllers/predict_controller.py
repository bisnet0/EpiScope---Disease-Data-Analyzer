import os
from flask import request, jsonify


from backend.modules.core_agent.services.predict_service import (
    predict_and_audit_service,
)


def handle_prediction_request():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]

    if not file or not file.filename:
        return jsonify({"error": "Arquivo inválido ou sem nome"}), 400

    filename = str(file.filename)

    model_type = str(request.form.get("type", "xray"))

    temp_dir = os.path.join(os.getcwd(), "backend", "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    temp_path = os.path.join(temp_dir, filename)
    file.save(temp_path)

    try:
        full_result = predict_and_audit_service(temp_path, model_type)

        return jsonify(full_result), 200
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
