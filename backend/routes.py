# backend/routes.py
from flask import Blueprint
from flask_jwt_extended import jwt_required
from backend.controllers.auth_controller import register_user, login_user, get_current_user_info
from backend.controllers.diagnose_controller import analyze_arbovirus, structure_symptoms_only, analyze_glaucoma

# Cria um Blueprint para agrupar as rotas
api_bp = Blueprint('api', __name__)

# --- Rotas de Autenticação ---
api_bp.route("/auth/register", methods=["POST"])(register_user)
api_bp.route("/auth/login", methods=["POST"])(login_user)
api_bp.route("/auth/me", methods=["GET"])(jwt_required()(get_current_user_info))

# --- Rotas de Diagnóstico (Arboviroses) ---
api_bp.route("/diagnose", methods=["POST"])(analyze_arbovirus)
api_bp.route("/structure-symptoms", methods=["POST"])(structure_symptoms_only)

# --- Rotas de Diagnóstico (Glaucoma) ---
api_bp.route("/diagnose-glaucoma", methods=["POST"])(analyze_glaucoma)