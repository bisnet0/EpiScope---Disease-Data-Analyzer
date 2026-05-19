import json
from backend.conftest import login

def test_diagnosis_flow(client, create_user):
    """Testa se a IA processa os sintomas e devolve análise."""
    login(client, "tester@epi.com", "123456")

    payload = {
        "text_description": "Febre alta e dores musculares.",
        "save_history": False,
        "age": 30,
        "sex": "M",
    }

    # Como agora as rotas estão modulares, ele vai bater no endpoint específico de predição/workflow
    response = client.post(
        "/diagnose/workflow", 
        data=json.dumps(payload), 
        content_type="application/json"
    )

    if response.status_code == 404:
        # Fallback de segurança do seu código original
        response = client.post(
            "/diagnose/predict-audit",
            data=json.dumps(payload),
            content_type="application/json",
        )

    if response.status_code != 200:
        print(f"\n❌ Erro Diagnose: {response.data}")

    assert response.status_code == 200
    data = json.loads(response.data)

    chaves_validas = ["analysis_details", "result", "probabilities", "recommendation", "data"]
    encontrou_chave = any(key in data for key in chaves_validas)

    if not encontrou_chave:
        print(f"\n⚠️ JSON Recebido: {data.keys()}")

    assert encontrou_chave