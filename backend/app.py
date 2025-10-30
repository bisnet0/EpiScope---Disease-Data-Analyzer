# backend/app.py (VERSÃO 7 - Add Glaucoma Endpoint)
import os
import joblib
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
import pandas as pd
import re
from flask_cors import CORS
import xgboost # Explicit import can help joblib
import numpy as np
# --- MUDANÇA: Imports for CNN ---
import tensorflow as tf
from PIL import Image # Pillow for image loading
import io # To read image from bytes
import cv2 # OpenCV might still be needed if Pillow fails or for specific ops
# --- FIM DA MUDANÇA ---


load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Paths for Models/Artifacts ---
ARTIFACTS_DIR = "/app/model_artifacts"

# Arbovirus Model Paths
ARBO_MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'xgboost_model.joblib')
ARBO_COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, 'model_columns.json')
ARBO_TARGET_MAP_PATH = os.path.join(ARTIFACTS_DIR, 'target_map.json')

# --- MUDANÇA: Glaucoma Model Paths ---
GLAUCOMA_MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'glaucoma_cnn_model.h5')
GLAUCOMA_INFO_PATH = os.path.join(ARTIFACTS_DIR, 'glaucoma_info.json')
# --- FIM DA MUDANÇA ---


# --- CONFIGURAÇÃO E CARREGAMENTO ---
# Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel('gemini-2.5-flash')
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    print(f"ERRO: Falha ao configurar o Gemini. Verifique a GEMINI_API_KEY. Erro: {e}")
    model_gemini = None

# Arbovirus Model
try:
    arbo_ml_model = joblib.load(ARBO_MODEL_PATH)
    with open(ARBO_COLUMNS_PATH, 'r') as f:
        arbo_model_columns = json.load(f)
    with open(ARBO_TARGET_MAP_PATH, 'r') as f:
        arbo_target_map = {int(k): v for k, v in json.load(f).items()}
    print(f"Modelo Arbovirus (XGBoost) carregado com sucesso.")
except Exception as e:
    print(f"ERRO: Artefatos do modelo Arbovirus não encontrados. Execute o train_arbovirus_model.py. Erro: {e}")
    arbo_ml_model, arbo_model_columns, arbo_target_map = None, None, None

# --- MUDANÇA: Load Glaucoma Model ---
try:
    glaucoma_cnn_model = tf.keras.models.load_model(GLAUCOMA_MODEL_PATH)
    with open(GLAUCOMA_INFO_PATH, 'r') as f:
        glaucoma_info = json.load(f)
    GLAUCOMA_IMG_SIZE = glaucoma_info.get("image_size", 224) # Default to 224 if not found
    GLAUCOMA_CLASS_NAMES = glaucoma_info.get("label_encoding", ['Normal', 'Glaucomatous']) # Get the ordered labels
    print(f"Modelo Glaucoma (CNN) carregado. Image Size: {GLAUCOMA_IMG_SIZE}, Classes: {GLAUCOMA_CLASS_NAMES}")
except Exception as e:
    print(f"ERRO: Artefatos do modelo Glaucoma não encontrados. Execute o train_cnn_glaucoma.py. Erro: {e}")
    glaucoma_cnn_model = None
    GLAUCOMA_IMG_SIZE = 224
    GLAUCOMA_CLASS_NAMES = ['Normal', 'Glaucomatous']
# --- FIM DA MUDANÇA ---

# --- Helper Functions (parse_json, get_symptom_list, convert_numpy_floats are the same) ---
def parse_json_from_gemini_response(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match: json_str = match.group(1)
    else: json_str = text
    try: return json.loads(json_str)
    except json.JSONDecodeError: return None

def get_symptom_list_from_cols(cols):
    symptoms = []
    for col in cols:
        if col not in ['sexo_encoded', 'idade', 'doenca_alvo', 'target_encoded']:
             symptoms.append(col)
    return symptoms

def convert_numpy_floats(data):
    if isinstance(data, dict): return {k: convert_numpy_floats(v) for k, v in data.items()}
    elif isinstance(data, list): return [convert_numpy_floats(item) for item in data]
    elif isinstance(data, (np.float32, np.float64)): return float(data)
    elif isinstance(data, (np.int32, np.int64)): return int(data)
    return data

# --- MUDANÇA: Preprocessing function for Glaucoma images ---
def preprocess_glaucoma_image(image_bytes, target_size=(GLAUCOMA_IMG_SIZE, GLAUCOMA_IMG_SIZE)):
    """Loads image from bytes, preprocesses for Glaucoma CNN."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB') # Load with Pillow, ensure RGB
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized)
        img_normalized = img_array / 255.0
        # Add batch dimension -> (1, IMG_SIZE, IMG_SIZE, 3)
        img_batch = np.expand_dims(img_normalized, axis=0)
        return img_batch
    except Exception as e:
        print(f"Erro ao pré-processar imagem para Glaucoma: {e}")
        return None
# --- FIM DA MUDANÇA ---


# --- ROTA ARBOVÍRUS (/diagnose) - Mantida igual à V6 ---
@app.route('/diagnose', methods=['POST'])
def diagnose_arbovirus():
    # Check if models are loaded
    if not all([arbo_ml_model, arbo_model_columns, arbo_target_map, model_gemini]):
        return jsonify({"error": "Modelo Arbovirus ou Gemini não carregado."}), 500

    input_data = request.get_json()
    if not input_data: return jsonify({"error": "Corpo JSON não fornecido."}), 400

    text_description = input_data.get('text_description')
    age = input_data.get('age')
    sex = input_data.get('sex')
    if not all([text_description, age, sex]):
        return jsonify({"error": "'text_description', 'age', 'sex' são obrigatórios."}), 400

    # 1: Structure symptoms
    symptom_list = get_symptom_list_from_cols(arbo_model_columns)
    prompt_structured = f"Analise: \"{text_description}\". Extraia sintomas em JSON. Possíveis: {str(symptom_list)}. true/false."
    response_structured = model_gemini.generate_content(prompt_structured)
    structured_symptoms = parse_json_from_gemini_response(response_structured.text)
    if not structured_symptoms: return jsonify({"error": "IA não estruturou sintomas."}), 500

    # 2: Prepare DataFrame
    try:
        input_df = pd.DataFrame(columns=arbo_model_columns, index=[0]).fillna(0)
        for symptom, present in structured_symptoms.items():
            if symptom in arbo_model_columns and present: input_df.loc[0, symptom] = 1
        input_df.loc[0, 'idade'] = age
        input_df.loc[0, 'sexo_encoded'] = 1 if sex.upper() == 'F' else 0
        input_df = input_df[arbo_model_columns] # Ensure column order
    except Exception as e: return jsonify({"error": f"Erro ao preparar dados: {str(e)}"}), 500

    # 3: Predict probabilities
    try:
        prediction_probabilities = arbo_ml_model.predict_proba(input_df)[0]
        results = {arbo_target_map[i]: prob for i, prob in enumerate(prediction_probabilities)}
    except AttributeError: # Fallback
         prediction = arbo_ml_model.predict(input_df)[0]
         results = {arbo_target_map[i]: (1.0 if i == prediction else 0.0) for i in arbo_target_map}
         print("AVISO: Usando predict() para Arbovirus.")

    # 4: Generate friendly response
    sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
    prob_text = "\n".join([f"* **{d.capitalize()}:** {p:.1%}" for d, p in sorted_results])
    top_disease = sorted_results[0][0].capitalize()
    prompt_friendly = f"Você é assistente EpiScope. Paciente: {age} anos, {sex}. Sintomas: \"{text_description}\". Modelo (XGBoost) previu:\n{prob_text}\nInterprete o resultado ({top_disease} mais provável?), mencione se probs são próximas. Enfatize: **NÃO É DIAGNÓSTICO MÉDICO, PROCURE UM MÉDICO.**"
    response_friendly = model_gemini.generate_content(prompt_friendly)

    # Convert before jsonify
    results_serializable = convert_numpy_floats(results)
    input_features_serializable = convert_numpy_floats(input_df.to_dict(orient='records')[0])

    return jsonify({
        "friendly_response": response_friendly.text,
        "analysis_details": {
            "probabilities": results_serializable,
            "structured_symptoms": structured_symptoms,
            "input_features": input_features_serializable
        }
    })

# --- ROTA STRUCTURE SYMPTOMS - Mantida ---
@app.route('/structure-symptoms', methods=['POST'])
def structure_symptoms():
    if not model_gemini or not arbo_model_columns:
        return jsonify({"error": "Modelo Gemini ou colunas Arbovirus não carregados."}), 500
    # ... (resto da função igual à V6) ...
    input_data = request.get_json()
    text_description = input_data.get('text_description')
    if not text_description: return jsonify({"error": "'text_description' não fornecido."}), 400
    try:
        symptom_list_for_prompt = get_symptom_list_from_cols(arbo_model_columns)
        prompt_structured = f"Analise: \"{text_description}\". Extraia sintomas JSON. Possíveis: {str(symptom_list_for_prompt)}. true/false."
        response_structured = model_gemini.generate_content(prompt_structured)
        structured_symptoms = parse_json_from_gemini_response(response_structured.text)
        if not structured_symptoms: return jsonify({"error": "IA não estruturou sintomas."}), 500
        return jsonify(structured_symptoms)
    except Exception as e: return jsonify({"error": f"Erro na IA: {str(e)}"}), 500


# --- MUDANÇA: NOVA ROTA PARA GLAUCOMA ---
@app.route('/diagnose-glaucoma', methods=['POST'])
def diagnose_glaucoma():
    if not glaucoma_cnn_model or not model_gemini:
        return jsonify({"error": "Modelo Glaucoma CNN ou Gemini não carregado."}), 500

    if 'image' not in request.files: return jsonify({"error": "Nenhum arquivo de imagem enviado."}), 400
    file = request.files['image']
    if file.filename == '': return jsonify({"error": "Nome de arquivo vazio."}), 400
    try: image_bytes = file.read()
    except Exception as e: return jsonify({"error": f"Erro ao ler arquivo: {str(e)}"}), 500

    processed_image = preprocess_glaucoma_image(image_bytes)
    if processed_image is None: return jsonify({"error": "Falha ao pré-processar a imagem."}), 500

    try:
        # --- LÓGICA DE PREDIÇÃO CORRIGIDA ---
        # No treino: ['Glaucomatous', 'Normal'] -> [0, 1]
        # O modelo (sigmoid) prevê a probabilidade da classe 1 (Normal)
        prediction_raw = glaucoma_cnn_model.predict(processed_image)[0]
        prob_normal = float(prediction_raw[0])
        prob_glaucomatous = 1.0 - prob_normal
        
        # Mapeia de volta para os nomes das classes
        results = {
            GLAUCOMA_CLASS_NAMES[0]: prob_glaucomatous, # 'Glaucomatous'
            GLAUCOMA_CLASS_NAMES[1]: prob_normal      # 'Normal'
        }

        # Determina a classe e confiança
        if prob_normal >= 0.5:
            predicted_class_name = "Normal"
            confidence = prob_normal
        else:
            predicted_class_name = "Glaucomatous"
            confidence = prob_glaucomatous
        # --- FIM DA CORREÇÃO ---

    except Exception as e:
        print(f"Erro durante predição da CNN: {e}"); import traceback; traceback.print_exc()
        return jsonify({"error": f"Erro ao executar modelo CNN: {str(e)}"}), 500

    # 4. Gerar Resposta Amigável (Gemini)
    prob_text = "\n".join([f"* **{name}:** {prob:.1%}" for name, prob in sorted(results.items(), key=lambda item: item[1], reverse=True)])

    prompt_friendly = f"""
    Você é um assistente de saúde virtual para o "EpiScope", um projeto acadêmico.
    Sua função é interpretar os resultados de um modelo CNN (MobileNetV2 Fine-Tuned) treinado para detectar Glaucoma em imagens de fundo de olho e comunicá-los de forma clara e segura.

    **Contexto da Análise:**
    * **Exame:** Imagem de fundo de olho (retinografia).
    * **Objetivo:** Análise preliminar para Glaucoma.
    * **Modelo de ML:** CNN (MobileNetV2 Fine-Tuned) treinado com o dataset Drishti-GS.

    **Resultado Preliminar do Modelo de ML:**
    {prob_text}

    **Sua Tarefa (Gerar a Resposta Amigável):**
    Escreva uma resposta profissional e amigável em português brasileiro.

    1.  Comece com uma saudação (Ex: "Olá! Recebemos sua imagem para análise.").
    2.  Explique que o modelo de IA do EpiScope analisou a imagem.
    3.  Apresente as probabilidades calculadas (usando o `{prob_text}`).
    4.  **Interprete o resultado:**
        * Destaque a condição mais provável ({predicted_class_name}) e sua confiança ({confidence:.1%}).
        * **NÃO afirme que a pessoa TEM ou NÃO TEM Glaucoma.** Use frases como "o modelo indica uma probabilidade de X%" ou "os achados são mais compatíveis com Y".
    5.  **Próximo Passo:** Independentemente do resultado, explique que esta análise é **PRELIMINAR** e que o diagnóstico de Glaucoma só pode ser feito por um **médico oftalmologista** após exames completos.
    6.  **DISCLAIMER (OBRIGATÓRIO):** Reforce que é um modelo **acadêmico**, **NÃO um diagnóstico**, e a necessidade **ABSOLUTA** de consultar um oftalmologista.

    Gere apenas a resposta para o paciente.
    """
    response_friendly = model_gemini.generate_content(prompt_friendly)
    
    return jsonify({
        "friendly_response": response_friendly.text,
        "analysis_details": {
            "probabilities": results, # Já é serializável
            "predicted_class": predicted_class_name,
            "confidence": confidence # Já é float
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)