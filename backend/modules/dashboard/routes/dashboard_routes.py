from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando a função pura do controller recém-limpo
from backend.modules.dashboard.controllers.dashboard_controller import (
    get_dashboard_stats
)

# Criamos o Blueprint com o prefixo do Dashboard
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# Rota protegida pelo JWT (a URL completa será /dashboard/stats)
dashboard_bp.route("/stats", methods=["GET"])(
    jwt_required()(get_dashboard_stats)
)