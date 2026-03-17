# backend/routes.py
from flask import Blueprint
from flask_jwt_extended import jwt_required
from backend.controllers.auth_controller import (
    register_user, 
    login_user, 
    get_current_user_info, 
    refresh_access_token, 
    logout_user
)
from backend.controllers.diagnose_controller import (
    analyze_arbovirus, 
    structure_symptoms_only, 
    analyze_glaucoma, 
    run_experiment, 
    get_ai_suggestion,
    get_user_history,
    run_evolutionary_optimization,
    run_glaucoma_evolution,
    analyze_xray
)
from backend.controllers.agent_controller import agent_bp

from backend.controllers.dashboard_controller import get_dashboard_stats

api_bp = Blueprint('api', __name__)

# Rotas de Autenticação
api_bp.route("/auth/register", methods=["POST"])(register_user)
api_bp.route("/auth/login", methods=["POST"])(login_user)
api_bp.route("/auth/logout", methods=["POST"])(logout_user) # Nova rota
# Importante: refresh=True exige o Refresh Token Cookie
api_bp.route("/auth/refresh", methods=["POST"])(jwt_required(refresh=True)(refresh_access_token)) 
api_bp.route("/auth/me", methods=["GET"])(jwt_required()(get_current_user_info))

# Rotas de Diagnóstico (Protegidas por Access Token Cookie)
api_bp.route("/diagnose", methods=["POST"])(jwt_required()(analyze_arbovirus))
api_bp.route("/structure-symptoms", methods=["POST"])(jwt_required()(structure_symptoms_only))
api_bp.route("/diagnose-glaucoma", methods=["POST"])(jwt_required()(analyze_glaucoma))
api_bp.route("/diagnose/experiment", methods=["POST"])(jwt_required()(run_experiment))
api_bp.route("/diagnose/advisor", methods=["GET"])(jwt_required()(get_ai_suggestion))
api_bp.route("/diagnose/history", methods=["GET"])(jwt_required()(get_user_history))
api_bp.route("/diagnose/optimize-ga", methods=["POST"])(jwt_required()(run_evolutionary_optimization))
api_bp.route("/diagnose/glaucoma/optimize-ga", methods=["POST"])(jwt_required()(run_glaucoma_evolution))
api_bp.route("/diagnose-xray", methods=["POST"])(jwt_required()(analyze_xray))

# Rota do Dashboard
api_bp.route("/dashboard/stats", methods=["GET"])(jwt_required()(get_dashboard_stats))

# Rotas do Agente Dr. EpiScope
api_bp.register_blueprint(agent_bp, url_prefix='/agent')

