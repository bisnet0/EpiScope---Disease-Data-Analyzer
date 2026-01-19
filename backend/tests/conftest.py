import pytest
from backend.app import app
from backend.models.user_model import db


@pytest.fixture
def client():
    """
    Cria um cliente de teste com banco ISOLADO em memória.
    """

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            yield client

            db.session.remove()
            db.drop_all()
