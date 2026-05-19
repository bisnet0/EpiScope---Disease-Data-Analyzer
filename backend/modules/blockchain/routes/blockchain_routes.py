from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando a função pura do controller
from backend.modules.blockchain.controllers.blockchain_controller import (
    register_blockchain_ledger
)

# Criamos o Blueprint com o prefixo
blockchain_bp = Blueprint("blockchain", __name__, url_prefix="/blockchain")

# Rota protegida pelo JWT (a URL completa será /blockchain/register)
blockchain_bp.route("/register", methods=["POST"])(
    jwt_required()(register_blockchain_ledger)
)