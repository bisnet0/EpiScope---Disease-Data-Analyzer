from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando os controllers recém-movidos para a pasta glaucoma
from backend.modules.glaucoma.controllers.glaucoma_controller import (
    analyze_glaucoma,
    run_glaucoma_evolution
)

# Criamos o Blueprint específico para Glaucoma
glaucoma_bp = Blueprint("glaucoma", __name__)

# Rotas protegidas (Mantendo as URLs exatas)
glaucoma_bp.route("/diagnose-glaucoma", methods=["POST"])(
    jwt_required()(analyze_glaucoma)
)
glaucoma_bp.route("/diagnose/optimize-ga", methods=["POST"])(
    jwt_required()(run_glaucoma_evolution)
)