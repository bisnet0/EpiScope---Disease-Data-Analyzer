from flask import Blueprint
from flask_jwt_extended import jwt_required
from backend.modules.profile.controllers.profile_controller import get_profile, update_profile

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

profile_bp.route("/", methods=["GET"])(jwt_required()(get_profile))
profile_bp.route("/", methods=["PUT", "PATCH"])(jwt_required()(update_profile))