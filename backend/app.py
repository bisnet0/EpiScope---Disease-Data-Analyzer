from datetime import timedelta
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from backend.models.user_model import db
from backend.models.diagnosis_model import ArbovirusDiagnosis, GlaucomaDiagnosis
from backend.routes import api_bp 
from backend.models.ml_log_model import ModelTrainingLog

load_dotenv()

app = Flask(__name__)

# --- CORS LIMPO E CORRETO ---
# Usamos apenas a lib. Sem after_request manual.
# origins: Lista com a URL exata do front (sem barra no final)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

# Configurações
# permite sobrescrever diretamente via variável de ambiente (útil para testes)
if os.getenv("SQLALCHEMY_DATABASE_URI"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT Cookies
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"] 
app.config["JWT_COOKIE_SECURE"] = False 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

# Inicialização
db.init_app(app)
jwt = JWTManager(app)

# Rotas
app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)