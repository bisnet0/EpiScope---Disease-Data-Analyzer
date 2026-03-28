from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando as funções puras do controller recém-limpo
from backend.modules.integrations.controllers.google_fit_controller import (
    google_fit_login,
    google_fit_callback,
    google_fit_status,
    sync_google_data,
    get_metrics
)

# Criamos o Blueprint com o prefixo
google_fit_bp = Blueprint("google_fit", __name__, url_prefix="/google_fit")

# Rotas protegidas pelo JWT
google_fit_bp.route("/login", methods=["GET"])(jwt_required()(google_fit_login))
google_fit_bp.route("/status", methods=["GET"])(jwt_required()(google_fit_status))
google_fit_bp.route("/sync", methods=["POST"])(jwt_required()(sync_google_data))
google_fit_bp.route("/metrics", methods=["GET"])(jwt_required()(get_metrics))

# O Callback fica SEM proteção JWT pois é um webhook redirecionado do Google
google_fit_bp.route("/callback", methods=["GET"])(google_fit_callback)