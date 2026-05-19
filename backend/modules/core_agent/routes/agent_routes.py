from flask import Blueprint
from flask_jwt_extended import jwt_required

# 👇 Importando as funções puras do controller recém-limpo
from backend.modules.core_agent.controllers.agent_controller import (
    chat_agent,
    get_chat_history
)

# Criamos o Blueprint com o prefixo do Agente
agent_bp = Blueprint("agent", __name__, url_prefix="/agent")

# Rotas mapeadas de forma explícita e protegidas
agent_bp.route("/chat", methods=["POST"])(jwt_required()(chat_agent))
agent_bp.route("/history", methods=["GET"])(jwt_required()(get_chat_history))