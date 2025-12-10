from flask import request, jsonify
from backend.services.ai_service import run_arbovirus_pipeline, run_glaucoma_pipeline, run_symptom_structure

def analyze_arbovirus():
    data = request.get_json()
    if not data: return jsonify({"error": "JSON inválido"}), 400
    
    desc = data.get("text_description")
    age = data.get("age")
    sex = data.get("sex")

    if not all([desc, age, sex]):
        return jsonify({"error": "Faltando dados (text_description, age, sex)"}), 400
    
    # Chama o Service
    result, status = run_arbovirus_pipeline(desc, age, sex)
    return jsonify(result), status

def structure_symptoms_only():
    data = request.get_json()
    desc = data.get("text_description")
    if not desc: return jsonify({"error": "Faltando text_description"}), 400
    
    result, status = run_symptom_structure(desc)
    return jsonify(result), status

def analyze_glaucoma():
    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Arquivo vazio"}), 400

    # Passa os bytes da imagem para o Service
    result, status = run_glaucoma_pipeline(file.read())
    return jsonify(result), status