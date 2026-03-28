from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando o controller recém-movido
from backend.modules.chest_xray.controllers.xray_controller import analyze_xray

# Criamos o Blueprint específico para Raio-X
xray_bp = Blueprint("xray", __name__)

# Rota protegida (Mantendo a URL exata /diagnose-xray)
xray_bp.route("/diagnose-xray", methods=["POST"])(
    jwt_required()(analyze_xray)
)