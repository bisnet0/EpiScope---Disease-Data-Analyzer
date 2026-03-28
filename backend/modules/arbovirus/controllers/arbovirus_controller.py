from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

# 👇 Imports mantidos apontando para os serviços antigos até refatorarmos a camada de service
from backend.controllers.workflow_controller import run_hospital_workflow_internal
from backend.services.ai_service import (
    run_arbovirus_pipeline,
    run_symptom_structure,
    run_genetic_pipeline,
)

def analyze_arbovirus():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    desc = data.get("text_description")
    age = data.get("age")
    sex = data.get("sex")

    if not all([desc, age, sex]):
        return jsonify({"error": "Faltando dados"}), 400

    result, status = run_arbovirus_pipeline(desc, age, sex, current_user_id)

    if status in [200, 201]:
        prediction_text = result.get("prediction", "Dengue")

        maestro_payload = {
            "diagnosis": f"Resultado IA: {prediction_text} | Relato do Paciente: {desc}"
        }

        print(f"🦟 [ARBO]: Enviando contexto real para o Maestro...")
        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if maestro_res:
            result["maestro_status"] = "PENDING_SIGNATURE"
            result["needs_emergency"] = maestro_res.get("needs_emergency", False)

    return jsonify(result), status


def structure_symptoms_only():
    data = request.get_json()
    desc = data.get("text_description")
    if not desc:
        return jsonify({"error": "Faltando text_description"}), 400

    result, status = run_symptom_structure(desc)
    return jsonify(result), status


def run_evolutionary_optimization():
    current_user_id = get_jwt_identity()

    data = request.get_json()
    model_type = data.get("model_type", "xgboost")

    ga_config = {
        "generations": int(data.get("generations", 5)),
        "population_size": int(data.get("population_size", 10)),
        "mutation_rate": float(data.get("mutation_rate", 0.1)),
        "crossover_rate": float(data.get("crossover_rate", 0.7)),
    }

    result, status = run_genetic_pipeline(model_type, current_user_id, ga_config)

    return jsonify(result), status