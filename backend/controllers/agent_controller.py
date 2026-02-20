from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from langchain_core.messages import HumanMessage
from backend.agents.graph import app_graph
from backend.models.chat_model import ChatMessage
from backend.models.user_model import db

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat_agent():
    user_id = get_jwt_identity()
    data = request.get_json()

    user_message = data.get("message", "")
    attachment_b64 = data.get("attachment")

    if not user_message and not attachment_b64:
        return jsonify({"error": "Mensagem vazia"}), 400

    try:
        audit_user_msg = ChatMessage(
            user_id=user_id,
            role="user",
            content=user_message,
            has_attachment=bool(attachment_b64),
        )
        db.session.add(audit_user_msg)
        db.session.commit()

        agent_input = user_message
        if attachment_b64:
            agent_input += f"\n\n[IMAGEM ANEXADA]: {attachment_b64}"

        inputs = {"messages": [HumanMessage(content=agent_input)]}
        final_state = app_graph.invoke(inputs, config={"recursion_limit": 10})

        raw_content = final_state["messages"][-1].content

        if isinstance(raw_content, list):
            ai_response = "\n".join(
                [
                    item.get("text", "")
                    for item in raw_content
                    if isinstance(item, dict) and "text" in item
                ]
            )
        else:
            ai_response = str(raw_content)

        audit_agent_msg = ChatMessage(
            user_id=user_id,
            role="agent",
            content=ai_response,
        )
        db.session.add(audit_agent_msg)
        db.session.commit()

        return jsonify(
            {"response": ai_response, "msg_id": audit_agent_msg.id, "status": "success"}
        ), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro no Agente: {e}")
        return jsonify({"error": "Erro interno no Dr. EpiScope"}), 500


@agent_bp.route("/history", methods=["GET"])
@jwt_required()
def get_chat_history():
    """Retorna o histórico para popular o chat ao abrir o botão flutuante"""
    user_id = get_jwt_identity()
    try:
        messages = (
            ChatMessage.query.filter_by(user_id=user_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(50)
            .all()
        )

        return jsonify([msg.to_dict() for msg in messages]), 200
    except Exception as e:
        return jsonify({"error": "Falha ao carregar histórico"}), 500
