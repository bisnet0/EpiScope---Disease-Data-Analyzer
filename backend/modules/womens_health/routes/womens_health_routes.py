from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.modules.womens_health.controllers.womens_health_controller import (
    analyze_womens_audio,
    analyze_womens_video,
    get_integrated_report,
    analyze_laparoscopy_video,
    update_cycle_profile,
    get_cycle_prediction,
)

womens_health_bp = Blueprint("womens_health", __name__)


womens_health_bp.route("/analyze-audio", methods=["POST"])(
    jwt_required()(analyze_womens_audio)
)
womens_health_bp.route("/analyze-video", methods=["POST"])(
    jwt_required()(analyze_womens_video)
)
womens_health_bp.route("/analyze-surgery", methods=["POST"])(
    jwt_required()(analyze_laparoscopy_video)
)
womens_health_bp.route("/get-report", methods=["GET"])(
    jwt_required()(get_integrated_report)
)
womens_health_bp.route("/cycle-profile", methods=["PUT", "POST"])(
    jwt_required()(update_cycle_profile)
)
womens_health_bp.route("/cycle-prediction", methods=["GET"])(
    jwt_required()(get_cycle_prediction)
)
