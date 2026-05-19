from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando os controllers da casa nova!
from backend.modules.arbovirus.controllers.arbovirus_controller import (
    analyze_arbovirus,
    structure_symptoms_only,
    run_evolutionary_optimization,
)

# Criamos o Blueprint específico para Arbovírus
arbovirus_bp = Blueprint("arbovirus", __name__)

# Rotas (Mantendo as URLs exatas para não quebrar o Front)
arbovirus_bp.route("/diagnose", methods=["POST"])(
    jwt_required()(analyze_arbovirus)
)
arbovirus_bp.route("/structure-symptoms", methods=["POST"])(
    jwt_required()(structure_symptoms_only)
)
arbovirus_bp.route("/diagnose/optimize-ga", methods=["POST"])(
    jwt_required()(run_evolutionary_optimization)
)