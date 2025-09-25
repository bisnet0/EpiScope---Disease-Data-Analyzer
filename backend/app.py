# backend/app.py
import os
import joblib
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
import pandas as pd
import re

load_dotenv()

# --- Funções Auxiliares (sem alteração) ---
def parse_json_from_gemini_response(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON da resposta do Gemini.")
        return None

def preprocess_for_model(symptoms_json, model_columns):
    input_df = pd.DataFrame(columns=model_columns, index=[0]).fillna(0)
    for symptom, present in symptoms_json.items():
        if symptom in input_df.columns and present:
            input_df[symptom] = 1
    return input_df

# --- Configuração do App ---
app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_gemini = genai.GenerativeModel('gemini-pro')

# --- Carregamento dos Artefatos do Modelo (Atualizado) ---
try:
    ml_model = joblib.load('decision_tree_model.joblib')
    with open('model_columns.json', 'r') as f:
        model_columns = json.load(f)
    with open('target_map.json', 'r') as f:
        # As chaves do JSON são strings, convertemos para inteiros
        target_map = {int(k): v for k, v in json.load(f).items()}
    print("Modelo de ML e artefatos carregados com sucesso.")
except FileNotFoundError:
    print("ERRO: Artefatos do modelo não encontrados. Execute o script de treinamento primeiro.")
    ml_model = None

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if not ml_model:
        return jsonify({"error": "Modelo de ML não está carregado."}), 500

    data = request.json
    symptoms_text = data.get('symptoms')
    if not symptoms_text:
        return jsonify({"error": "Texto de sintomas não fornecido"}), 400

    # --- Controller 2: Estruturar dados com IA (Prompt Atualizado) ---
    prompt_structured = f"""
    Analise o seguinte texto de um paciente e extraia os sintomas em formato JSON.
    Os possíveis sintomas são: 'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea', 'dor_costas', 'conjuntvit', 'artrite', 'artralgia', 'petequia_n', 'leucopenia', 'dor_retro'.
    O JSON de saída deve ter chaves para cada sintoma e o valor deve ser true se o sintoma for mencionado, e false caso contrário.
    Texto do paciente: "{symptoms_text}"
    JSON de saída:
    """
    response_structured = model_gemini.generate_content(prompt_structured)
    structured_symptoms = parse_json_from_gemini_response(response_structured.text)
    if not structured_symptoms:
        return jsonify({"error": "Não foi possível estruturar os sintomas a partir do texto."}), 500

    # --- Controller 3: Executar modelo de ML (Lógica Atualizada) ---
    input_data_for_ml = preprocess_for_model(structured_symptoms, model_columns)
    prediction_probabilities = ml_model.predict_proba(input_data_for_ml)[0]
    
    # NOVO: Mapeando probabilidades para os nomes das doenças
    results = {target_map[i]: prob for i, prob in enumerate(prediction_probabilities)}
    
    # --- Controller 4: Gerar resposta amigável com IA (Prompt Atualizado) ---
    prob_text = "\n".join([f"- {disease.capitalize()}: {prob:.0%}" for disease, prob in results.items()])
    prompt_friendly = f"""
    Você é um assistente de saúde virtual. Com base na análise de sintomas de um paciente, as probabilidades de diagnóstico para as seguintes arboviroses são:
    {prob_text}
    
    Sintomas relatados: "{symptoms_text}"

    Escreva uma resposta profissional, amigável e coesa. **Importante: Enfatize que isso não é um diagnóstico médico definitivo e que a pessoa deve procurar um médico para confirmação.**
    """
    response_friendly = model_gemini.generate_content(prompt_friendly)
    
    return jsonify({
        "analysis": {
            "probabilities": results,
            "friendly_response": response_friendly.text
        },
        "structured_symptoms": structured_symptoms
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)