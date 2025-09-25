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

# --- Funções Auxiliares para a API ---
def parse_json_from_gemini_response(text):
    """Extrai uma string JSON de dentro de uma resposta de texto, mesmo que tenha ```json ... ```."""
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Se não encontrar o bloco de código, assume que a resposta inteira é o JSON
        json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON da resposta do Gemini.")
        return None

def preprocess_for_model(symptoms_json, model_columns):
    """Transforma o JSON de sintomas em um DataFrame no formato exato que o modelo espera."""
    # Cria um DataFrame com uma linha, preenchido com zeros, e com as colunas do modelo
    input_df = pd.DataFrame(columns=model_columns, index=[0]).fillna(0)

    # Preenche o DataFrame com os sintomas recebidos (ex: cs_sexo_M, sg_uf_not_SP, etc.)
    # ATENÇÃO: Esta é uma implementação simplificada. A lógica real dependerá
    # das features que seu modelo usa (sexo, idade, estado, etc).
    # O exemplo abaixo assume que as features do modelo são os próprios sintomas.
    # Você terá que adaptar esta parte para corresponder às features do seu `model_columns.json`
    
    for symptom, present in symptoms_json.items():
        if symptom in input_df.columns and present:
            input_df[symptom] = 1
            
    return input_df

# --- Configuração do App ---
app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_gemini = genai.GenerativeModel('gemini-pro')

# --- Carregamento dos Artefatos do Modelo ---
try:
    ml_model = joblib.load('decision_tree_model.joblib')
    with open('model_columns.json', 'r') as f:
        model_columns = json.load(f)
    print("Modelo de ML e colunas carregados com sucesso.")
except FileNotFoundError:
    print("ERRO: 'decision_tree_model.joblib' ou 'model_columns.json' não encontrado. Execute o script de treinamento primeiro.")
    ml_model = None
    model_columns = []

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if not ml_model:
        return jsonify({"error": "Modelo de ML não está carregado."}), 500

    data = request.json
    symptoms_text = data.get('symptoms')

    if not symptoms_text:
        return jsonify({"error": "Texto de sintomas não fornecido"}), 400

    # --- Controller 2: Estruturar dados com IA ---
    prompt_structured = f"""
    Analise o seguinte texto de um paciente e extraia os sintomas em formato JSON. 
    Os possíveis sintomas são: 'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea', 'dor_costas', 'conjutivite', 'artrite', 'artralgia', 'petequia_n', 'leucopenia', 'dor_retro'.
    O JSON de saída deve ter chaves para cada sintoma e o valor deve ser true se o sintoma for mencionado, e false caso contrário.
    Texto do paciente: "{symptoms_text}"
    JSON de saída:
    """
    response_structured = model_gemini.generate_content(prompt_structured)
    structured_symptoms = parse_json_from_gemini_response(response_structured.text)

    if not structured_symptoms:
        return jsonify({"error": "Não foi possível estruturar os sintomas a partir do texto."}), 500

    # --- Controller 3: Executar modelo de ML ---
    # ATENÇÃO: O modelo foi treinado para prever Zika (Confirmado/Inconclusivo).
    # A resposta da API deve refletir isso. O ideal seria treinar um modelo multiclasse.
    # Por enquanto, vamos adaptar a resposta para o modelo atual.
    
    # input_data_for_ml = preprocess_for_model(structured_symptoms, model_columns)
    # prediction_probabilities = ml_model.predict_proba(input_data_for_ml)[0]
    
    # results = {
    #     'Probabilidade_Inconclusivo': prediction_probabilities[0],
    #     'Probabilidade_Zika_Confirmado': prediction_probabilities[1],
    # }

    # --- Controller 4: Gerar resposta amigável com IA ---
    # prompt_friendly = f"""
    # Você é um assistente de saúde virtual. Com base na análise de sintomas de um paciente, as probabilidades de diagnóstico para Zika Vírus são:
    # - Probabilidade de ser um caso de Zika: {results['Probabilidade_Zika_Confirmado']:.0%}
    # - Probabilidade de ser inconclusivo com base nos dados: {results['Probabilidade_Inconclusivo']:.0%}
    # Sintomas relatados: "{symptoms_text}"
    # Escreva uma resposta profissional, amigável e coesa. **Importante: Enfatize que isso não é um diagnóstico médico definitivo e que a pessoa deve procurar um médico.**
    # """
    # response_friendly = model_gemini.generate_content(prompt_friendly)
    
    # --- Resposta Final ---
    # Simplificando a resposta por enquanto, pois o modelo não prevê as 3 doenças.
    return jsonify({
        "received_text": symptoms_text,
        "structured_symptoms": structured_symptoms,
        # "analysis": {
        #     "probabilities": results,
        #     "friendly_response": response_friendly.text
        # }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)