from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando o controller da nova pasta do módulo blockchain
from backend.modules.blockchain.controllers.blockchain_controller import register_blockchain_ledger

# Criamos o Blueprint com o prefixo /blockchain
blockchain_bp = Blueprint("blockchain", __name__, url_prefix="/blockchain")

# Rota protegida (Como já temos o prefixo, aqui fica só /register)
blockchain_bp.route("/register", methods=["POST"])(
    jwt_required()(register_blockchain_ledger)
)