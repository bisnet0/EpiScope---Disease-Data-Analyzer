# backend/controllers/diagnose_controller.py
import os
import joblib
import json
import pandas as pd
import tensorflow as tf
import google.generativeai as genai
from flask import request, jsonify
from backend.utils.data_helpers import (
    parse_json_from_gemini_response, 
    get_symptom_list_from_cols, 
    convert_numpy_floats, 
    preprocess_glaucoma_image
)

# --- CARREGAMENTO GLOBAL DOS MODELOS (SINGLETON) ---
ARTIFACTS_DIR = "/app/model_artifacts"
print("--- Inicializando Controllers de IA ---")

# 1. Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Erro Gemini: {e}")
    model_gemini = None

# 2. Arboviroses (XGBoost)
try:
    arbo_ml_model = joblib.load(os.path.join(ARTIFACTS_DIR, "xgboost_model.joblib"))
    with open(os.path.join(ARTIFACTS_DIR, "model_columns.json"), "r") as f:
        arbo_model_columns = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "target_map.json"), "r") as f:
        arbo_target_map = {int(k): v for k, v in json.load(f).items()}
except Exception:
    arbo_ml_model = None

# 3. Glaucoma (CNN)
try:
    glaucoma_cnn_model = tf.keras.models.load_model(os.path.join(ARTIFACTS_DIR, "glaucoma_cnn_model.h5"))
    with open(os.path.join(ARTIFACTS_DIR, "glaucoma_info.json"), "r") as f:
        g_info = json.load(f)
    GLAUCOMA_CLASS_NAMES = g_info.get("class_names", ["Normal", "Glaucomatous"])
    GLAUCOMA_IMG_SIZE = g_info.get("image_size", 224)
except Exception:
    glaucoma_cnn_model = None
    GLAUCOMA_CLASS_NAMES = ["Normal", "Glaucomatous"]


# --- FUNÇÕES DO CONTROLLER ---

def analyze_arbovirus():
    if not arbo_ml_model or not model_gemini:
        return jsonify({"error": "Modelos indisponíveis"}), 500
    
    data = request.get_json()
    desc, age, sex = data.get("text_description"), data.get("age"), data.get("sex")
    
    # 1. Gemini estrutura os sintomas
    symptoms_list = get_symptom_list_from_cols(arbo_model_columns)
    prompt = f'Analise: "{desc}". JSON true/false para: {symptoms_list}.'
    structured = parse_json_from_gemini_response(model_gemini.generate_content(prompt).text)
    
    # 2. Prepara DataFrame
    df = pd.DataFrame(columns=arbo_model_columns, index=[0]).fillna(0)
    for s, v in structured.items():
        if s in df.columns and v: df.loc[0, s] = 1
    df.loc[0, "idade"] = age
    df.loc[0, "sexo_encoded"] = 1 if sex.upper() == "F" else 0
    
    # 3. Predição
    probs = arbo_ml_model.predict_proba(df[arbo_model_columns])[0]
    results = {arbo_target_map[i]: prob for i, prob in enumerate(probs)}
    
    # 4. Gemini interpreta (Amigável)
    top_d = max(results, key=results.get)
    res_txt = "\n".join([f"{k}: {v:.1%}" for k,v in results.items()])
    friendly = model_gemini.generate_content(f"Explique p/ paciente: {age} anos. Sintomas: {desc}. Probabilidades: {res_txt}. Mais provável: {top_d}. USE DISCLAIMER MÉDICO.").text
    
    return jsonify({
        "friendly_response": friendly,
        "analysis_details": {
            "probabilities": convert_numpy_floats(results),
            "structured_symptoms": structured
        }
    })

def structure_symptoms_only():
    if not model_gemini: return jsonify({"error": "Gemini off"}), 500
    desc = request.get_json().get("text_description")
    symptoms = get_symptom_list_from_cols(arbo_model_columns)
    resp = model_gemini.generate_content(f'Analise: "{desc}". JSON true/false para: {symptoms}.')
    return jsonify(parse_json_from_gemini_response(resp.text))

def analyze_glaucoma():
    if not glaucoma_cnn_model: return jsonify({"error": "CNN off"}), 500
    if "image" not in request.files: return jsonify({"error": "Sem imagem"}), 400
    
    img_batch = preprocess_glaucoma_image(request.files["image"].read(), (GLAUCOMA_IMG_SIZE, GLAUCOMA_IMG_SIZE))
    pred = glaucoma_cnn_model.predict(img_batch)[0][0] # Sigmoid output
    
    prob_normal = float(pred)
    prob_glaucoma = 1.0 - prob_normal
    results = {GLAUCOMA_CLASS_NAMES[0]: prob_glaucoma, GLAUCOMA_CLASS_NAMES[1]: prob_normal} # [0]=Glaucomatous, [1]=Normal (da encoding)
    
    # Lógica inversa (verificar encoding no treino): Se LabelEncoder deu Glaucoma=0, Normal=1
    # Sigmoid -> 1 é Normal.
    
    friendly = model_gemini.generate_content(f"Analise de Glaucoma. Probabilidades: {results}. Explique que é PRELIMINAR. Consulte oftalmologista.").text
    
    return jsonify({
        "friendly_response": friendly,
        "analysis_details": {"probabilities": results}
    })