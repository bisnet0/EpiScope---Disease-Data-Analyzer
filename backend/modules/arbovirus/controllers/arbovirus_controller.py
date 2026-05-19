from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from typing import Dict, Any, cast


from backend.modules.core_agent.controllers.workflow_controller import (
    run_hospital_workflow_internal,
)
from backend.modules.arbovirus.services.arbovirus_service import (
    run_arbovirus_pipeline,
    run_symptom_structure,
)

from backend.modules.laboratory.services.laboratory_service import run_genetic_pipeline


def analyze_arbovirus():
    current_user_id = str(get_jwt_identity())

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "JSON inválido"}), 400

    desc = data.get("text_description")
    age = data.get("age")
    sex = data.get("sex")

    if desc is None or age is None or sex is None:
        return jsonify({"error": "Faltando dados"}), 400

    try:
        age_int = int(age)
    except (ValueError, TypeError):
        return jsonify({"error": "Idade inválida"}), 400

    result, status = run_arbovirus_pipeline(
        str(desc), age_int, str(sex), current_user_id
    )

    if status in [200, 201] and isinstance(result, dict):
        analysis_details = result.get("analysis_details")
        if isinstance(analysis_details, dict):
            prediction_text = analysis_details.get("winner_model", "Dengue")
        else:
            prediction_text = result.get("prediction", "Dengue")

        maestro_payload = {
            "diagnosis": f"Resultado IA: {prediction_text} | Relato do Paciente: {desc}"
        }

        print(f"🦟 [ARBO]: Enviando contexto real para o Maestro...")
        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if isinstance(maestro_res, dict):
            result["maestro_status"] = "PENDING_SIGNATURE"
            result["needs_emergency"] = maestro_res.get("needs_emergency", False)

    return jsonify(result), status


def structure_symptoms_only():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "JSON inválido"}), 400

    desc = data.get("text_description")
    if not desc:
        return jsonify({"error": "Faltando text_description"}), 400

    result, status = run_symptom_structure(str(desc))
    return jsonify(result), status


def run_evolutionary_optimization():
    current_user_id = str(get_jwt_identity())

    data = request.get_json()
    if not isinstance(data, dict):
        data = {}

    model_type = str(data.get("model_type", "xgboost"))

    ga_config = {
        "generations": int(data.get("generations", 5)),
        "population_size": int(data.get("population_size", 10)),
        "mutation_rate": float(data.get("mutation_rate", 0.1)),
        "crossover_rate": float(data.get("crossover_rate", 0.7)),
    }

    result, status = run_genetic_pipeline(model_type, current_user_id, ga_config)

    return jsonify(result), status
