from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando as funções puras do controller recém-limpo
from backend.modules.integrations.controllers.strava_controller import (
    sync_strava,
    get_strava_activities,
    strava_login,
    strava_callback,
    strava_status
)

# Criamos o Blueprint com o prefixo
strava_bp = Blueprint("strava", __name__, url_prefix="/strava")

# Rotas do Strava mapeadas de forma explícita e elegante
strava_bp.route("/sync", methods=["POST"])(jwt_required()(sync_strava))
strava_bp.route("/activities", methods=["GET"])(jwt_required()(get_strava_activities))
strava_bp.route("/login", methods=["GET"])(jwt_required()(strava_login))
strava_bp.route("/status", methods=["GET"])(jwt_required()(strava_status))

# O Callback fica SEM proteção JWT pois é um webhook redirecionado do Strava
strava_bp.route("/callback", methods=["GET"])(strava_callback)