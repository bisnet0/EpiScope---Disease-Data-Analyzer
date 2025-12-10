import os
import joblib
import json
import pandas as pd
import tensorflow as tf
import google.generativeai as genai
from backend.utils.data_helpers import (
    parse_json_from_gemini_response, 
    get_symptom_list_from_cols, 
    convert_numpy_floats, 
    preprocess_glaucoma_image
)

# --- CARREGAMENTO DOS MODELOS (SINGLETON NO SERVICE) ---
ARTIFACTS_DIR = "/app/model_artifacts"
print("--- Inicializando AI Service ---")

# 1. Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Erro Gemini: {e}")
    model_gemini = None

# 2. Arboviroses
try:
    arbo_ml_model = joblib.load(os.path.join(ARTIFACTS_DIR, "xgboost_model.joblib"))
    with open(os.path.join(ARTIFACTS_DIR, "model_columns.json"), "r") as f:
        arbo_model_columns = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "target_map.json"), "r") as f:
        arbo_target_map = {int(k): v for k, v in json.load(f).items()}
except Exception:
    arbo_ml_model = None
    arbo_model_columns = []

# 3. Glaucoma
try:
    glaucoma_cnn_model = tf.keras.models.load_model(os.path.join(ARTIFACTS_DIR, "glaucoma_cnn_model.h5"))
    with open(os.path.join(ARTIFACTS_DIR, "glaucoma_info.json"), "r") as f:
        g_info = json.load(f)
    GLAUCOMA_CLASS_NAMES = g_info.get("class_names", ["Normal", "Glaucomatous"])
    GLAUCOMA_IMG_SIZE = g_info.get("image_size", 224)
except Exception:
    glaucoma_cnn_model = None
    GLAUCOMA_CLASS_NAMES = ["Normal", "Glaucomatous"]
    GLAUCOMA_IMG_SIZE = 224


# --- LÓGICA DE ARBOVIROSES ---
def run_arbovirus_pipeline(text_description, age, sex):
    if not arbo_ml_model or not model_gemini:
        return {"error": "Serviço de IA indisponível (Modelos não carregados)"}, 503

    # 1. Estruturação via Gemini
    symptoms_list = get_symptom_list_from_cols(arbo_model_columns)
    prompt = f'Analise: "{text_description}". Extraia sintomas JSON true/false. Possíveis: {symptoms_list}.'
    try:
        gemini_resp = model_gemini.generate_content(prompt)
        structured = parse_json_from_gemini_response(gemini_resp.text)
        if not structured: raise ValueError("Falha ao estruturar JSON")
    except Exception as e:
        return {"error": f"Erro na IA Generativa: {str(e)}"}, 500

    # 2. Preparar DataFrame
    try:
        df = pd.DataFrame(columns=arbo_model_columns, index=[0]).fillna(0)
        for s, v in structured.items():
            if s in df.columns and v: df.loc[0, s] = 1
        df.loc[0, "idade"] = age
        df.loc[0, "sexo_encoded"] = 1 if sex.upper() == "F" else 0
        
        # 3. Predição XGBoost
        probs = arbo_ml_model.predict_proba(df[arbo_model_columns])[0]
        results = {arbo_target_map[i]: prob for i, prob in enumerate(probs)}
    except Exception as e:
        return {"error": f"Erro na Predição Numérica: {str(e)}"}, 500

    # 4. Interpretação Amigável
    try:
        top_d = max(results, key=results.get)
        res_txt = "\n".join([f"{k}: {v:.1%}" for k,v in results.items()])
        prompt_friendly = f"Explique para paciente ({age} anos): Sintomas: {text_description}. Probabilidades: {res_txt}. Mais provável: {top_d}. USE DISCLAIMER: NÃO É DIAGNÓSTICO."
        friendly = model_gemini.generate_content(prompt_friendly).text
    except Exception:
        friendly = "Erro ao gerar explicação amigável. Consulte os dados brutos."

    return {
        "friendly_response": friendly,
        "analysis_details": {
            "probabilities": convert_numpy_floats(results),
            "structured_symptoms": structured
        }
    }, 200

def run_symptom_structure(text_description):
    if not model_gemini: return {"error": "Gemini off"}, 503
    symptoms = get_symptom_list_from_cols(arbo_model_columns)
    resp = model_gemini.generate_content(f'Analise: "{text_description}". JSON true/false: {symptoms}.')
    return parse_json_from_gemini_response(resp.text), 200


# --- LÓGICA DE GLAUCOMA ---
def run_glaucoma_pipeline(image_bytes):
    if not glaucoma_cnn_model: return {"error": "Modelo CNN off"}, 503
    
    img_batch = preprocess_glaucoma_image(image_bytes, (GLAUCOMA_IMG_SIZE, GLAUCOMA_IMG_SIZE))
    if img_batch is None: return {"error": "Imagem inválida"}, 400

    try:
        pred = glaucoma_cnn_model.predict(img_batch)[0][0]
        prob_normal = float(pred)
        prob_glaucoma = 1.0 - prob_normal
        results = {GLAUCOMA_CLASS_NAMES[0]: prob_glaucoma, GLAUCOMA_CLASS_NAMES[1]: prob_normal}
        
        friendly = model_gemini.generate_content(
            f"Analise Glaucoma. Prob: {results}. Explique PRELIMINAR. Consulte oftalmo."
        ).text
    except Exception as e:
        return {"error": f"Erro no processamento da imagem: {e}"}, 500

    return {
        "friendly_response": friendly,
        "analysis_details": {"probabilities": results}
    }, 200