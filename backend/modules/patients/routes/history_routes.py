from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando o controller recém-movido para a pasta patients
from backend.modules.patients.controllers.history_controller import get_user_history

# Criamos o Blueprint específico para o Histórico do Paciente
history_bp = Blueprint("history", __name__)

# Rota protegida (Mantendo a URL exata para o front continuar puxando a timeline)
history_bp.route("/diagnose/history", methods=["GET"])(
    jwt_required()(get_user_history)
)