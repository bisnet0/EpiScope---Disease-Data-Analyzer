# backend/app.py
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from backend.models.user_model import db
from backend.routes import api_bp # Importa o arquivo único de rotas

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurações
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")

# Inicialização
db.init_app(app)
jwt = JWTManager(app)

# Registra as rotas
app.register_blueprint(api_bp)

# Cria tabelas ao iniciar (apenas para dev/teste)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)