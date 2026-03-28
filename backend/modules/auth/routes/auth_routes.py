from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando as funções puras do controller recém-limpo
from backend.modules.auth.controllers.auth_controller import (
    register_user,
    login_user,
    logout_user,
    refresh_access_token,
    get_current_user_info
)

# Criamos o Blueprint com o prefixo
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Rotas Públicas
auth_bp.route("/register", methods=["POST"])(register_user)
auth_bp.route("/login", methods=["POST"])(login_user)

# Rotas Protegidas
auth_bp.route("/logout", methods=["POST"])(logout_user)

# Importante: refresh=True exige o Refresh Token Cookie
auth_bp.route("/refresh", methods=["POST"])(jwt_required(refresh=True)(refresh_access_token))

# Rota de Perfil
auth_bp.route("/me", methods=["GET"])(jwt_required()(get_current_user_info))