from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.services.ai_service import (
    run_arbovirus_pipeline,
    run_glaucoma_pipeline,
    run_symptom_structure,
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
