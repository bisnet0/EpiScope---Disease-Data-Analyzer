import json
import pytest
from backend.app import app
# 👇 Imports atualizados para a nova arquitetura
from backend.modules.auth.models.user_model import db, User

@pytest.fixture(scope="session", autouse=True)
def guard_db():
    """
    TRAVA DE SEGURANÇA: Impede que testes rodem no banco de produção/dev.
    """
    db_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")

    if "postgresql" in db_url and ":memory:" not in db_url:
        pytest.exit(
            "\n🚨 PERIGO: Tentativa de rodar testes no Banco de Produção (Postgres)! \nCancelando para evitar perda de dados. Configure o env SQLALCHEMY_DATABASE_URI para sqlite:///:memory:",
            returncode=1,
        )

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        if "sqlite" not in str(db.engine.url):
            pytest.fail("O teste falhou em isolar o banco. Abortando para segurança.")

        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

# 👇 Fixtures Globais de Autenticação (agora disponíveis para todos os módulos)
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