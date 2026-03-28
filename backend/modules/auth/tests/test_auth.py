import json
# Importamos a função auxiliar global (se o Pytest não injetar automaticamente, você pode importar do conftest)
from backend.conftest import login

def test_login_flow(client, create_user):
    """Verifica se o login retorna 200 OK e mensagem de sucesso."""
    response = login(client, "tester@epi.com", "123456")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "user" in data