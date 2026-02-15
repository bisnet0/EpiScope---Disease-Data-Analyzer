from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from langchain_core.messages import HumanMessage
from backend.agents.graph import app_graph

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat_agent():
    """
    Endpoint principal do Agente Dr. EpiScope.
    Entrada: { "message": "Tenho febre..." }
    Saída: { "response": "O diagnóstico é..." }
    """
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Mensagem vazia"}), 400

    try:
        # Configuração para manter histórico (Opcional: aqui poderíamos carregar do DB)
        # Por enquanto, é stateless por requisição (ou o frontend manda o histórico)
        inputs = {"messages": [HumanMessage(content=user_message)]}
        
        # Invoca o Agente
        # O recursion_limit evita loops infinitos se ele se perder
        final_state = app_graph.invoke(inputs, config={"recursion_limit": 10})
        
        # Pega a última resposta da IA
        ai_response = final_state["messages"][-1].content
        
        return jsonify({
            "response": ai_response,
            "status": "success"
        }), 200

    except Exception as e:
        print(f"Erro no Agente: {e}")
        return jsonify({"error": "Erro interno no Dr. EpiScope", "details": str(e)}), 500