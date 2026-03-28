from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando o controller da nova pasta do módulo de dashboard
from backend.modules.dashboard.controllers.dashboard_controller import get_dashboard_stats

# Criamos o Blueprint com o prefixo /dashboard
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# Rota (Como já temos o prefixo, aqui fica só /stats)
dashboard_bp.route("/stats", methods=["GET"])(
    jwt_required()(get_dashboard_stats)
)