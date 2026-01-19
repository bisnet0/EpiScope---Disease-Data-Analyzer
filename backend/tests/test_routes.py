import json
import pytest
from backend.models.user_model import User
from backend.models.user_model import db


@pytest.fixture
def create_user(client):
    db.session.query(User).delete()
    db.session.commit()

    user = User(username="tester", email="tester@epi.com")
    user.set_password("123456")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, password):
    return client.post(
        "/auth/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )


def test_login_flow(client, create_user):
    """Verifica se o login retorna 200 OK e mensagem de sucesso."""
    response = login(client, "tester@epi.com", "123456")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "user" in data


def test_dashboard_access(client, create_user):
    """Prova que o cookie de login permite acessar áreas restritas."""

    resp_anon = client.get("/dashboard/stats")
    assert resp_anon.status_code == 401

    login(client, "tester@epi.com", "123456")

    resp_auth = client.get("/dashboard/stats?period=all&model=all")

    if resp_auth.status_code != 200:
        print(f"\n❌ Erro Dash: {resp_auth.data}")

    assert resp_auth.status_code == 200
    data = json.loads(resp_auth.data)

    assert "kpis" in data
    assert "ga_analysis" in data["charts"]


def test_diagnosis_flow(client, create_user):
    """Testa se a IA processa os sintomas e devolve análise."""
    login(client, "tester@epi.com", "123456")

    payload = {
        "text_description": "Febre alta e dores musculares.",
        "save_history": False,
        "age": 30,
        "sex": "M",
    }

    response = client.post(
        "/diagnose", data=json.dumps(payload), content_type="application/json"
    )

    if response.status_code == 404:
        response = client.post(
            "/diagnose/arbovirus",
            data=json.dumps(payload),
            content_type="application/json",
        )

    if response.status_code != 200:
        print(f"\n❌ Erro Diagnose: {response.data}")

    assert response.status_code == 200
    data = json.loads(response.data)

    chaves_validas = ["analysis_details", "result", "probabilities", "recommendation"]
    encontrou_chave = any(key in data for key in chaves_validas)

    if not encontrou_chave:
        print(f"\n⚠️ JSON Recebido: {data.keys()}")

    assert encontrou_chave
