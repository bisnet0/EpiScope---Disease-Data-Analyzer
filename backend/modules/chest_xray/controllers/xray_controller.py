from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
# Retiramos a importação do Dict e Any, não vamos mais precisar forçar a barra!

# 👇 Imports mantidos para os caminhos antigos até a refatoração total
from backend.modules.core_agent.controllers.workflow_controller import run_hospital_workflow_internal
from backend.modules.chest_xray.services.xray_service import run_xray_pipeline

def analyze_xray():
    current_user_id = get_jwt_identity()

    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem de Raio-X enviada"}), 400

    file = request.files["image"]

    result, status = run_xray_pipeline(file.read(), str(current_user_id))

    if status in [200, 201] and isinstance(result, dict):
        pred = result.get("prediction", "Normal")
        
        # 👇 TYPE GUARD ANINHADO: Verificando cada nível do dicionário
        analysis_details = result.get("analysis_details")
        if not isinstance(analysis_details, dict):
            analysis_details = {}
            
        probabilities = analysis_details.get("probabilities")
        if not isinstance(probabilities, dict):
            probabilities = {}
            
        prob_pneumonia = probabilities.get("Pneumonia", 0)

        risk_label = (
            "URGENTE - INFILTRADO ALVEOLAR" if pred == "Pneumonia" else "Normal"
        )

        # Garantindo que prob_pneumonia possa ser convertido para float com segurança
        try:
            prob_float = float(prob_pneumonia)
        except (ValueError, TypeError):
            prob_float = 0.0

        maestro_payload = {
            "diagnosis": f"Raio-X de Tórax: {pred} ({prob_float * 100:.1f}%). Status: {risk_label}."
        }

        print(f"🫁 [X-RAY]: Maestro analisando pulmões...")
        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if isinstance(maestro_res, dict):
            result["maestro_status"] = "PENDING_SIGNATURE"
            result["needs_emergency"] = maestro_res.get("needs_emergency", False)

    return jsonify(result), status