from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

# 👇 Imports mantidos para os caminhos antigos até a refatoração total
from backend.controllers.workflow_controller import run_hospital_workflow_internal
from backend.services.ai_service import run_xray_pipeline

def analyze_xray():
    """
    Recebe a imagem de Raio-X via form-data, envia para a CNN
    e aciona o Maestro para orquestração clínica.
    """
    current_user_id = get_jwt_identity()

    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem de Raio-X enviada"}), 400

    file = request.files["image"]

    result, status = run_xray_pipeline(file.read(), current_user_id)

    if status in [200, 201]:
        pred = result.get("prediction", "Normal")
        prob_pneumonia = result.get("analysis_details", {}).get("probabilities", {}).get("Pneumonia", 0)

        risk_label = (
            "URGENTE - INFILTRADO ALVEOLAR" if pred == "Pneumonia" else "Normal"
        )

        maestro_payload = {
            "diagnosis": f"Raio-X de Tórax: {pred} ({prob_pneumonia * 100:.1f}%). Status: {risk_label}."
        }

        print(f"🫁 [X-RAY]: Maestro analisando pulmões...")
        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if maestro_res:
            result["maestro_status"] = "PENDING_SIGNATURE"
            result["needs_emergency"] = maestro_res.get("needs_emergency", False)

    return jsonify(result), status