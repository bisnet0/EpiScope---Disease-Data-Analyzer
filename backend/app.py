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

app = Flask(__name__)

# --- CONFIGURAÇÃO E CARREGAMENTO DOS MODELOS ---

# Configura a API do Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel('gemini-pro')
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    print(f"ERRO: Falha ao configurar o Gemini. Verifique a GEMINI_API_KEY. Erro: {e}")
    model_gemini = None

# Carrega o modelo de ML e os artefatos (colunas, mapa de alvo)
try:
    ml_model = joblib.load('decision_tree_model.joblib')
    with open('model_columns.json', 'r') as f:
        model_columns = json.load(f)
    with open('target_map.json', 'r') as f:
        target_map = {int(k): v for k, v in json.load(f).items()}
    print("Modelo de ML e artefatos carregados com sucesso.")
except Exception as e:
    print(f"ERRO: Artefatos do modelo de ML não encontrados. Execute o train_model.py. Erro: {e}")
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


# --- ROTA PRINCIPAL DA API ---
@app.route('/diagnose', methods=['POST'])
def diagnose():
    if not all([ml_model, model_columns, target_map, model_gemini]):
        return jsonify({"error": "Um ou mais modelos não estão carregados. Verifique os logs."}), 500

    # 1. Obter os dados de entrada completos
    input_data = request.get_json()
    if not input_data:
        return jsonify({"error": "Corpo da requisição JSON não fornecido."}), 400

    text_description = input_data.get('text_description')
    age = input_data.get('age')
    sex = input_data.get('sex')
    criteria_code = input_data.get('criteria_code')

    if not all([text_description, age, sex, criteria_code is not None]):
        return jsonify({"error": "Dados de entrada incompletos. 'text_description', 'age', 'sex' e 'criteria_code' são obrigatórios."}), 400

    # --- CONTROLLER 1: Estruturar sintomas com IA ---
    prompt_structured = f"""
    Analise o texto e extraia os sintomas em JSON. Sintomas possíveis: {str([c for c in model_columns if '_' not in c and c not in ['idade']])}.
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
        # Cria um DataFrame vazio com todas as colunas que o modelo espera, preenchido com 0
        input_df = pd.DataFrame(columns=model_columns, index=[0]).fillna(0)

        # Preenche os sintomas binarizados
        for symptom, present in structured_symptoms.items():
            if symptom in input_df.columns and present:
                input_df.loc[0, symptom] = 1

        # Preenche os dados demográficos
        input_df.loc[0, 'idade'] = age
        input_df.loc[0, 'sexo_encoded'] = 1 if sex.upper() == 'F' else 0

        # Preenche as features de critério (One-Hot Encoded)
        criterio_col = f'criterio_{criteria_code}'
        if criterio_col in input_df.columns:
            input_df.loc[0, criterio_col] = 1
        
        # Garante que a ordem das colunas está correta
        input_df = input_df[model_columns]

    except Exception as e:
        return jsonify({"error": f"Erro ao preparar dados para o modelo: {str(e)}"}), 500

    # --- CONTROLLER 3: Executar modelo de ML ---
    prediction_probabilities = ml_model.predict_proba(input_df)[0]
    results = {target_map[i]: prob for i, prob in enumerate(prediction_probabilities)}
    
    # --- CONTROLLER 4: Gerar resposta amigável com IA ---
    prob_text = "\n".join([f"- {disease.capitalize()}: {prob:.0%}" for disease, prob in results.items()])
    prompt_friendly = f"""
    Você é um assistente de saúde virtual. Com base na análise de um paciente de {age} anos, sexo {sex}, e sintomas relatados como "{text_description}", as probabilidades de diagnóstico são:
    {prob_text}
    
    Escreva uma resposta profissional e amigável. **Enfatize que este é um resultado de um modelo de IA, não um diagnóstico médico, e que a pessoa DEVE procurar um médico para confirmação.**
    """
    response_friendly = model_gemini.generate_content(prompt_friendly)
    
    return jsonify({
        "friendly_response": response_friendly.text,
        "analysis_details": {
            "probabilities": results,
            "structured_symptoms": structured_symptoms,
            "input_features": input_df.to_dict(orient='records')[0]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)