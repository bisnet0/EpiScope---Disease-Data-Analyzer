import os
import uuid
import base64

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.agents.graph import app_graph
from backend.models.chat_model import ChatMessage
from backend.models.user_model import db

agent_bp = Blueprint("agent", __name__)
TEMP_DIR = os.path.join(os.getcwd(), "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)


@agent_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat_agent():
    user_id = get_jwt_identity()
    data = request.get_json()

    user_message = data.get("message", "").strip()
    attachment_b64 = data.get("attachment")

    if not user_message and not attachment_b64:
        return jsonify({"error": "Mensagem vazia"}), 400

    if not user_message and attachment_b64:
        user_message = "Por favor, analise a imagem em anexo."

    try:
        past_msgs = (
            ChatMessage.query.filter_by(user_id=user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(8)
            .all()
        )
        past_msgs.reverse()

        langchain_history = []
        for m in past_msgs:
            if m.role == "user":
                langchain_history.append(HumanMessage(content=m.content))
            else:
                langchain_history.append(AIMessage(content=m.content))

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
            try:
                if "," in attachment_b64:
                    base64_data = attachment_b64.split(",")[1]
                else:
                    base64_data = attachment_b64

                temp_path = os.path.join(TEMP_DIR, f"img_{uuid.uuid4().hex}.png")
                with open(temp_path, "wb") as fh:
                    fh.write(base64.b64decode(base64_data))

                agent_input += f"\n\n[CAMINHO DO ARQUIVO PARA ANÁLISE]: {temp_path}"
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")

        system_prompt = """Você é o Dr. EpiScope, um Médico Pesquisador e Supervisor de IA de alto nível.
Regras de ouro:
1. CONTEXTO DE TRIAGEM: Você pode usar o histórico da conversa APENAS para lembrar dados demográficos (idade, sexo, nome) se já foram informados.
2. ISOLAMENTO DE EXAMES (REGRA ABSOLUTA): Cada imagem ou descrição de sintomas enviada é um NOVO CASO ou uma NOVA AVALIAÇÃO. Você é ESTRITAMENTE PROIBIDO de usar, deduzir ou reaproveitar resultados, laudos, porcentagens ou diagnósticos de mensagens anteriores para avaliar uma nova solicitação. Esqueça o laudo anterior ao analisar um novo.
3. EXECUÇÃO OBRIGATÓRIA DA FERRAMENTA: Ao receber uma nova imagem (indicada por [CAMINHO DO ARQUIVO PARA ANÁLISE]), você DEVE acionar a ferramenta correspondente (ex: xray_tool, glaucoma_tool) e basear seu diagnóstico clínico ÚNICA E EXCLUSIVAMENTE no retorno exato dessa execução atual. Nunca invente valores.
4. DUPLA VISÃO (ML + LITERATURA): Combine o resultado matemático exato retornado pela ferramenta de Machine Learning com a literatura médica pesquisada via `rag_clinical_tool`.
5. ESTRUTURA DA RESPOSTA: Forneça sempre a Visão Específica (o diagnóstico preditivo real) e a Visão Abrangente (literatura médica e diretrizes de tratamento).
6. BLOCKCHAIN E CARTESI: Você NÃO tem capacidade de registrar diagnósticos na blockchain diretamente. O registro exige a assinatura da carteira Web3 na aba "Assinatura". NUNCA simule registros on-chain."""
        messages_to_send = (
            [SystemMessage(content=system_prompt)]
            + langchain_history
            + [HumanMessage(content=agent_input)]
        )

        inputs = {"messages": messages_to_send}
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
            user_id=user_id, role="agent", content=ai_response
        )
        db.session.add(audit_agent_msg)
        db.session.commit()

        return jsonify(
            {"response": ai_response, "msg_id": audit_agent_msg.id, "status": "success"}
        ), 200

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)

        import traceback

        error_trace = traceback.format_exc()
        print(f"\n[ERRO FATAL NO AGENTE]:\n{error_trace}\n")

        if (
            "RESOURCE_EXHAUSTED" in error_msg
            or "429" in error_msg
            or "quota" in error_msg.lower()
        ):
            return jsonify(
                {
                    "error": "QUOTA_EXCEEDED",
                    "detalhes": "O limite de requisições da API do Google Gemini foi atingido.",
                }
            ), 429

        return jsonify(
            {"error": "Erro interno no Dr. EpiScope", "detalhes": str(e)}
        ), 500


@agent_bp.route("/history", methods=["GET"])
@jwt_required()
def get_chat_history():
    user_id = get_jwt_identity()

    try:
        past_msgs = (
            ChatMessage.query.filter_by(user_id=user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(50)
            .all()
        )

        past_msgs.reverse()

        history = []
        for m in past_msgs:
            history.append(
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "has_attachment": m.has_attachment,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
            )

        return jsonify(history), 200

    except Exception as e:
        print(f"Erro ao carregar histórico: {e}")
        return (jsonify({"error": "Erro ao carregar histórico do Dr. EpiScope"}),)
