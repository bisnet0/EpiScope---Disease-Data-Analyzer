from flask import Blueprint
from flask_jwt_extended import jwt_required

from backend.modules.core_agent.controllers.workflow_controller import run_hospital_workflow
# 👇 Ele já está importado e roteado aqui!
from backend.modules.core_agent.controllers.predict_controller import handle_prediction_request

workflow_bp = Blueprint("workflow", __name__)

workflow_bp.route("/diagnose/workflow", methods=["POST"])(jwt_required()(run_hospital_workflow))

# Rota já protegida e configurada perfeitamente:
workflow_bp.route("/diagnose/predict-audit", methods=["POST"])(
    jwt_required()(handle_prediction_request)
)