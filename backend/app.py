# backend/app.py (VERSÃO 6 - JSON Serialization Fix)
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
import numpy as np # Import numpy to check types

load_dotenv()

app = Flask(__name__)
CORS(app)

ARTIFACTS_DIR = "/app/model_artifacts"
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'xgboost_model.joblib')
COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, 'model_columns.json')
TARGET_MAP_PATH = os.path.join(ARTIFACTS_DIR, 'target_map.json')

# --- CONFIGURAÇÃO E CARREGAMENTO ---
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel('gemini-2.5-flash')
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    print(f"ERRO: Falha ao configurar o Gemini. Verifique a GEMINI_API_KEY. Erro: {e}")
    model_gemini = None

try:
    ml_model = joblib.load(MODEL_PATH)
    with open(COLUMNS_PATH, 'r') as f:
        model_columns = json.load(f)
    with open(TARGET_MAP_PATH, 'r') as f:
        target_map = {int(k): v for k, v in json.load(f).items()}
    print(f"Modelo de ML (XGBoost) e artefatos carregados com sucesso do volume '{ARTIFACTS_DIR}'.")
except Exception as e:
    print(f"ERRO: Artefatos do modelo de ML não encontrados em '{ARTIFACTS_DIR}'. Execute o train_model.py. Erro: {e}")
    ml_model, model_columns, target_map = None, None, None


# --- FUNÇÃO AUXILIAR ---
def parse_json_from_gemini_response(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON da resposta do Gemini: {text}")
        return None

def get_symptom_list_from_cols(cols):
    symptoms = []
    for col in cols:
        if col not in ['sexo_encoded', 'idade', 'doenca_alvo', 'target_encoded'] and 'criterio' not in col and 'ns1' not in col:
            symptoms.append(col)
    return symptoms

# --- MUDANÇA: Helper function to convert numpy floats ---
def convert_numpy_floats(data):
    """Recursively converts numpy float32/64 to Python float in dicts and lists."""
    if isinstance(data, dict):
        return {k: convert_numpy_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_floats(item) for item in data]
    elif isinstance(data, (np.float32, np.float64)):
        return float(data)
    elif isinstance(data, (np.int32, np.int64)): # Also handle numpy ints just in case
        return int(data)
    return data
# --- FIM DA MUDANÇA ---


# --- ROTA PRINCIPAL DA API ---
@app.route('/diagnose', methods=['POST'])
def diagnose():
    if not all([ml_model, model_columns, target_map, model_gemini]):
        return jsonify({"error": "Um ou mais modelos não estão carregados. Verifique os logs."}), 500

    input_data = request.get_json()
    if not input_data:
        return jsonify({"error": "Corpo da requisição JSON não fornecido."}), 400

    text_description = input_data.get('text_description')
    age = input_data.get('age')
    sex = input_data.get('sex')

    if not all([text_description, age, sex]):
        return jsonify({"error": "Dados de entrada incompletos. 'text_description', 'age' e 'sex' são obrigatórios."}), 400

    # --- CONTROLLER 1: Estruturar sintomas com IA ---
    symptom_list_for_prompt = get_symptom_list_from_cols(model_columns)
    prompt_structured = f"""
    Analise o texto e extraia os sintomas em JSON. Sintomas possíveis: {str(symptom_list_for_prompt)}.
    O valor deve ser true se o sintoma for mencionado, e false caso contrário.
    Texto: "{text_description}"
    JSON de saída:
    """
    response_structured = model_gemini.generate_content(prompt_structured)
    structured_symptoms = parse_json_from_gemini_response(response_structured.text)
    if not structured_symptoms:
        return jsonify({"error": "IA não conseguiu estruturar os sintomas a partir do texto."}), 500

    # --- CONTROLLER 2: Preparar o DataFrame para o modelo de ML ---
    try:
        input_df = pd.DataFrame(columns=model_columns, index=[0]).fillna(0)
        for symptom, present in structured_symptoms.items():
            # Only fill symptoms that are actual columns expected by the model
            if symptom in model_columns and present:
                input_df.loc[0, symptom] = 1
            # Add a check for unknown symptoms extracted by AI, maybe log them
            elif symptom not in model_columns and present:
                 print(f"AVISO: IA extraiu sintoma '{symptom}' não esperado pelo modelo. Ignorando.")

        input_df.loc[0, 'idade'] = age
        input_df.loc[0, 'sexo_encoded'] = 1 if sex.upper() == 'F' else 0

        # Ensure correct column order, dropping any extra cols the AI might have added
        input_df = input_df[model_columns]

    except Exception as e:
        return jsonify({"error": f"Erro ao preparar dados para o modelo: {str(e)}"}), 500

    # --- CONTROLLER 3: Executar modelo de ML ---
    try:
        prediction_probabilities = ml_model.predict_proba(input_df)[0]
        results = {target_map[i]: prob for i, prob in enumerate(prediction_probabilities)}
    except AttributeError:
         prediction = ml_model.predict(input_df)[0]
         results = {target_map[i]: (1.0 if i == prediction else 0.0) for i in target_map}
         print("AVISO: Usando predict() em vez de predict_proba() para XGBoost.")

    # --- CONTROLLER 4: Gerar resposta amigável com IA ---
    sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
    prob_text = "\n".join([f"* **{disease.capitalize()}:** {prob:.1%}" for disease, prob in sorted_results])
    top_disease = sorted_results[0][0].capitalize()

    prompt_friendly = f"""
    Você é um assistente de saúde virtual para o "EpiScope", um projeto acadêmico de pós-graduação.
    Sua função é interpretar os resultados de um modelo de Machine Learning (XGBoost) e comunicá-los ao paciente de forma clara, empática e, acima de tudo, segura.

    **Contexto da Análise do Paciente:**
    * **Paciente:** {age} anos, sexo {sex}.
    * **Sintomas Relatados:** "{text_description}"
    * **Sintomas Estruturados (extraídos por IA):** {json.dumps(structured_symptoms)}
    * **Modelo de ML:** XGBoost treinado com ~1.4 milhão de registros balanceados, usando APENAS sintomas e demografia.

    **Resultado do Modelo de ML:**
    {prob_text}

    **Sua Tarefa (Gerar a Resposta Amigável):**
    Escreva uma resposta profissional e amigável em português brasileiro.

    1.  Comece com uma saudação empática.
    2.  Explique que o modelo de IA fez uma análise preliminar.
    3.  Apresente a lista de probabilidades.
    4.  **Interprete o resultado:**
        * Destaque a doença mais provável.
        * **Se as probabilidades forem próximas**, mencione a similaridade dos sintomas e a necessidade de exames.
        * **Se uma probabilidade for alta**, mencione que é um **forte indicativo**, mas não certeza.
    5.  **DISCLAIMER (OBRIGATÓRIO):** Termine com o aviso de segurança (modelo acadêmico, NÃO diagnóstico, PROCURE UM MÉDICO).

    Gere apenas a resposta para o paciente.
    """
    response_friendly = model_gemini.generate_content(prompt_friendly)

    # --- MUDANÇA: Convert data types before jsonify ---
    # Convert probabilities (results) and input features just in case
    results_serializable = convert_numpy_floats(results)
    input_features_serializable = convert_numpy_floats(input_df.to_dict(orient='records')[0])
    # --- FIM DA MUDANÇA ---

    return jsonify({
        "friendly_response": response_friendly.text,
        "analysis_details": {
            "probabilities": results_serializable, # Use the converted dict
            "structured_symptoms": structured_symptoms,
            "input_features": input_features_serializable # Use the converted dict
        }
    })

@app.route('/structure-symptoms', methods=['POST'])
def structure_symptoms():
    # (Esta rota permanece a mesma da V4)
    if not model_gemini or not model_columns:
        return jsonify({"error": "Modelo Gemini ou colunas do modelo não estão carregados."}), 500
    input_data = request.get_json()
    text_description = input_data.get('text_description')
    if not text_description:
        return jsonify({"error": "'text_description' não fornecido."}), 400
    try:
        symptom_list_for_prompt = get_symptom_list_from_cols(model_columns)
        prompt_structured = f"""
        Analise o texto e extraia os sintomas em JSON. Sintomas possíveis: {str(symptom_list_for_prompt)}.
        O valor deve ser true se o sintoma for mencionado, e false caso contrário.
        Texto: "{text_description}"
        JSON de saída:
        """
        response_structured = model_gemini.generate_content(prompt_structured)
        structured_symptoms = parse_json_from_gemini_response(response_structured.text)
        if not structured_symptoms:
            return jsonify({"error": "IA não conseguiu estruturar os sintomas."}), 500
        return jsonify(structured_symptoms)
    except Exception as e:
        return jsonify({"error": f"Erro ao chamar a IA: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)