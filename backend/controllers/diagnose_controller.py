from datetime import timezone
from backend.models.diagnosis_model import (
    ArbovirusDiagnosis,
    GlaucomaDiagnosis,
    XRayDiagnosis,
)
from backend.controllers.workflow_controller import run_hospital_workflow_internal
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
    run_xray_pipeline,
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


def analyze_xray():
    current_user_id = get_jwt_identity()

    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem de Raio-X enviada"}), 400

    file = request.files["image"]

    result, status = run_xray_pipeline(file.read(), current_user_id)

    if status in [200, 201]:
        pred = result.get("prediction", "Normal")

        maestro_payload = {
            "diagnosis": f"Raio-X (Tórax) processado: {pred}",
            "severity": "HIGH" if "Pneumonia" in pred or "Opacidade" in pred else "LOW",
        }

        print(f"🫁 [X-RAY]: Disparando Maestro para auditoria...")

        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if maestro_res:
            result["maestro_status"] = "PENDING_SIGNATURE"

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

    if status == 200 or status == 201:
        pred = result.get("prediction", "Análise de Glaucoma")
        prob = result.get("probability", 0)

        maestro_payload = {
            "diagnosis": f"Glaucoma detectado via CNN. Probabilidade: {prob:.2f}% - {pred}",
            "severity": "HIGH" if prob > 0.5 else "LOW",
        }

        print(f"👁️ [GLAUCOMA]: Disparando Maestro para auditoria...")
        run_hospital_workflow_internal(maestro_payload)

        if maestro_payload:
            result["maestro_status"] = maestro_payload.get(
                "blockchain_ref", "PENDING_SIGNATURE"
            )
            result["maestro_id"] = maestro_payload.get("id")

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
    xray = XRayDiagnosis.query.filter_by(user_id=current_user_id).all()
    history = []

    for item in arbovirus:
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )

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
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )

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

    for item in xray:
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )

        history.append(
            {
                "id": item.id,
                "type": "RAIO-X (TÓRAX)",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": "Radiografia Pulmonar (Processada via CNN)",
                "result": item.prediction_result,
                "signature": tx_hash,
            }
        )

    history.sort(key=lambda x: x["date"], reverse=True)
    return jsonify(history), 200


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
