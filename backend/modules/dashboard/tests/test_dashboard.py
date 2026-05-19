import json
from backend.conftest import login

def test_dashboard_access(client, create_user):
    """Prova que o cookie de login permite acessar áreas restritas."""

    resp_anon = client.get("/dashboard/stats")
    assert resp_anon.status_code == 401

    login(client, "tester@epi.com", "123456")

    # Ajustado para usar a rota protegida modularizada
    resp_auth = client.get("/dashboard/stats?period=all&model=all")

    if resp_auth.status_code != 200:
        print(f"\n❌ Erro Dash: {resp_auth.data}")

    assert resp_auth.status_code == 200
    data = json.loads(resp_auth.data)

    assert "kpis" in data
    assert "ga_analysis" in data["charts"]