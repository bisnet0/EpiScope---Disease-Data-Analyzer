from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando os controllers da nova pasta do módulo core_agent
from backend.modules.core_agent.controllers.workflow_controller import run_hospital_workflow
from backend.modules.core_agent.controllers.predict_controller import handle_prediction_request

# Criamos o Blueprint para o Workflow Principal
workflow_bp = Blueprint("workflow", __name__)

# Rotas protegidas (Mantendo as URLs exatas)
workflow_bp.route("/diagnose/workflow", methods=["POST"])(
    jwt_required()(run_hospital_workflow)
)
workflow_bp.route("/diagnose/predict-audit", methods=["POST"])(
    jwt_required()(handle_prediction_request)
)