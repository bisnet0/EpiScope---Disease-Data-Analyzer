from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando os controllers da nova pasta do módulo
from backend.modules.womens_health.controllers.womens_health_controller import (
    analyze_womens_audio,
    analyze_womens_video
)

# Criamos o Blueprint específico
womens_health_bp = Blueprint("womens_health", __name__)

# Rotas protegidas (Mantendo as URLs exatas da Fase 4)
womens_health_bp.route("/womens-health/analyze-audio", methods=["POST"])(
    jwt_required()(analyze_womens_audio)
)
womens_health_bp.route("/womens-health/analyze-video", methods=["POST"])(
    jwt_required()(analyze_womens_video)
)