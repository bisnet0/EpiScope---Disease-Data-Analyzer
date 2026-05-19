from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando os controllers da pasta do laboratório
from backend.modules.laboratory.controllers.lab_controller import (
    run_experiment,
    get_ai_suggestion
)

# Criamos o Blueprint específico para os Experimentos
lab_bp = Blueprint("laboratory", __name__)

# Rotas protegidas (Mantendo as URLs exatas)
lab_bp.route("/diagnose/experiment", methods=["POST"])(
    jwt_required()(run_experiment)
)
lab_bp.route("/diagnose/advisor", methods=["GET"])(
    jwt_required()(get_ai_suggestion)
)