from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

# 👇 Imports temporários apontando para a estrutura antiga
from backend.modules.core_agent.controllers.workflow_controller import run_hospital_workflow_internal
from backend.modules.glaucoma.services.glaucoma_service import (
    run_glaucoma_pipeline,
    run_glaucoma_genetic_pipeline,
)


def analyze_glaucoma():
    current_user_id = get_jwt_identity()

    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Arquivo vazio"}), 400

    result, status = run_glaucoma_pipeline(file.read(), current_user_id)

    if status in [200, 201]:
        pred = result.get("prediction", "Glaucoma")
        prob = float(result.get("probability", 0))

        severity_label = "URGENTE/ALTA SEVERIDADE" if prob > 0.8 else "Monitoramento"

        maestro_payload = {
            "diagnosis": f"Análise de Glaucoma via CNN: {pred} com {prob:.2f}% de confiança. {severity_label}."
        }

        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if maestro_res:
            result["maestro_status"] = "PENDING_SIGNATURE"
            result["needs_emergency"] = maestro_res.get("needs_emergency", False)

    return jsonify(result), status


def run_glaucoma_evolution():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    model_type = data.get("model_type", "xgboost")

    ga_config = {
        "generations": int(data.get("generations", 5)),
        "population_size": int(data.get("population_size", 8)),
        "mutation_rate": float(data.get("mutation_rate", 0.1)),
        "crossover_rate": float(data.get("crossover_rate", 0.7)),
    }

    result, status = run_glaucoma_genetic_pipeline(
        model_type, current_user_id, ga_config
    )

    return jsonify(result), status