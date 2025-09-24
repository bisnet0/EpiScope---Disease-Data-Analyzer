# app.py
import os
import joblib
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Configuração do Flask e da API do Gemini
app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_gemini = genai.GenerativeModel('gemini-pro')

# Carregar o modelo de ML treinado
ml_model = joblib.load('decision_tree_model.joblib')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms_text = data.get('symptoms')

    if not symptoms_text:
        return jsonify({"error": "Texto de sintomas não fornecido"}), 400

    # --- Lógica do Controller 2: Estruturar dados com IA ---
    prompt_structured = f"""
    Analise o seguinte texto de um paciente e extraia os sintomas em formato JSON. 
    Os possíveis sintomas são: 'nauseas', 'dor_de_cabeca', 'cansaco', 'dor_nas_vistas', 'vermelhidao_na_pele', 'febre'.
    O JSON de saída deve ter chaves para cada sintoma e o valor deve ser true se o sintoma for mencionado, e false caso contrário.
    Texto do paciente: "{symptoms_text}"
    JSON de saída:
    """
    response_structured = model_gemini.generate_content(prompt_structured)
    # (Adicionar tratamento de erro e parsing do JSON da resposta aqui)
    structured_symptoms = parse_json_from_gemini_response(response_structured.text)

    # --- Lógica do Controller 3: Executar modelo de ML ---
    # (Transformar o JSON de sintomas em um formato que o modelo espera, ex: um array do Pandas)
    input_data_for_ml = preprocess_for_model(structured_symptoms)
    prediction_probabilities = ml_model.predict_proba(input_data_for_ml)[0]

    # Mapear probabilidades para as doenças
    results = {
        'Dengue': prediction_probabilities[0],
        'Zika': prediction_probabilities[1],
        'Chikungunya': prediction_probabilities[2],
    }

    # --- Lógica do Controller 4: Gerar resposta amigável com IA ---
    prompt_friendly = f"""
    Você é um assistente de saúde virtual. Com base na análise de sintomas de um paciente, as probabilidades de diagnóstico são:
    - Dengue: {results['Dengue']:.0%}
    - Zika: {results['Zika']:.0%}
    - Chikungunya: {results['Chikungunya']:.0%}

    Sintomas relatados: "{symptoms_text}"

    Escreva uma resposta profissional, amigável e coesa. **Importante: Enfatize que isso não é um diagnóstico médico definitivo e que a pessoa deve procurar um médico.**
    """
    response_friendly = model_gemini.generate_content(prompt_friendly)

    # --- Resposta Final ---
    return jsonify({
        "analysis": {
            "probabilities": results,
            "friendly_response": response_friendly.text
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)