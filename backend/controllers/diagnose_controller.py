from datetime import timezone
from backend.models.diagnosis_model import ArbovirusDiagnosis, GlaucomaDiagnosis
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.services.ai_service import (
    run_arbovirus_pipeline,
    run_glaucoma_genetic_pipeline,
    run_glaucoma_pipeline,
    run_symptom_structure,
    run_experiment_pipeline,
    get_best_optimization_suggestion,
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
        return jsonify({"error": "Faltando dados (text_description, age, sex)"}), 400

    result, status = run_arbovirus_pipeline(desc, age, sex, current_user_id)
    return jsonify(result), status


def structure_symptoms_only():
    data = request.get_json()
    desc = data.get("text_description")
    if not desc:
        return jsonify({"error": "Faltando text_description"}), 400

    result, status = run_symptom_structure(desc)
    return jsonify(result), status


def analyze_glaucoma():
    current_user_id = get_jwt_identity()

    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Arquivo vazio"}), 400

    result, status = run_glaucoma_pipeline(file.read(), current_user_id)
    return jsonify(result), status


def run_experiment():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    model_type = data.get("model_type")
    params = data.get("params")

    if not model_type or not params:
        return jsonify({"error": "Parâmetros ou tipo de modelo faltando"}), 400

    result, status = run_experiment_pipeline(current_user_id, model_type, params)
    return jsonify(result), status


def get_ai_suggestion():
    result, status = get_best_optimization_suggestion()
    return jsonify(result), status


def get_user_history():
    current_user_id = get_jwt_identity()

    arbovirus = ArbovirusDiagnosis.query.filter_by(user_id=current_user_id).all()
    glaucoma = GlaucomaDiagnosis.query.filter_by(user_id=current_user_id).all()

    history = []

    for item in arbovirus:
        tx_hash = getattr(item, "blockchain_hash", None)

        history.append(
            {
                "id": item.id,
                "type": "Arbovirose",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": f"Sintomas: {item.text_description[:40]}..."
                if item.text_description
                else "Descrição não disponível",
                "result": item.prediction_result,
                "signature": tx_hash,
            }
        )

    for item in glaucoma:
        tx_hash = getattr(item, "blockchain_hash", None)

        history.append(
            {
                "id": item.id,
                "type": "Glaucoma",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": "Imagem de Fundo de Olho (Processada)",
                "result": item.prediction_result,
                "signature": tx_hash,
            }
        )

    history.sort(key=lambda x: x["date"], reverse=True)

    return jsonify(history), 200


def run_evolutionary_optimization():
    data = request.get_json()
    model_type = data.get("model_type", "xgboost")

    ga_config = {
        "generations": data.get("generations", 5),
        "population_size": data.get("population_size", 10),
        "mutation_rate": data.get("mutation_rate", 0.1),
        "crossover_rate": data.get("crossover_rate", 0.7),
    }

    result, status = run_genetic_pipeline(model_type, ga_config)
    return jsonify(result), status


def run_glaucoma_evolution():
    data = request.get_json()
    model_type = data.get("model_type", "xgboost")

    result, status = run_glaucoma_genetic_pipeline(model_type)
    return jsonify(result), status
