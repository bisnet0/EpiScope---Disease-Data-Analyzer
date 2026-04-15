from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.modules.womens_health.controllers.womens_health_controller import (
    analyze_womens_audio,
    analyze_womens_video,
)

womens_health_bp = Blueprint("womens_health", __name__)

# O Flask vai somar: /api/womens-health + /analyze-audio
womens_health_bp.route("/analyze-audio", methods=["POST"])(
    jwt_required()(analyze_womens_audio)
)
womens_health_bp.route("/analyze-video", methods=["POST"])(
    jwt_required()(analyze_womens_video)
)