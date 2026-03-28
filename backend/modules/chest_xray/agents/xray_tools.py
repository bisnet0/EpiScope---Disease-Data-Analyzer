import os
import base64
from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain.tools import tool

# 👇 O import do ai_service temporário
from backend.services.ai_service import run_xray_pipeline

def get_safe_user_id():
    """Busca o usuário do Token (se API) ou o primeiro do banco (se Terminal)"""
    if has_request_context():
        try:
            return get_jwt_identity()
        except:
            pass

    from backend.models.user_model import User
    admin = User.query.first()
    return admin.id if admin else None


@tool("xray_tool")
def xray_tool(image_data: str = None):
    """
    Usa a Rede Neural Convolucional (CNN) para analisar imagens de Raio-X de Tórax (Chest X-Ray).
    A entrada 'image_data' DEVE ser o caminho do arquivo local ou uma string base64.
    USE ESTA FERRAMENTA SEMPRE que o usuário enviar uma imagem e perguntar se tem pneumonia,
    anomalia pulmonar, ou pedir para avaliar um raio-x.
    """
    print("\n[AGENTE] 🩻 Acionando o Radiologista de IA (CNN Raio-X)...")

    if image_data:
        try:
            # Puxa o ID real do paciente logado
            current_user_id = get_safe_user_id()
            if not current_user_id:
                return "Erro: Usuário não autenticado."

            if os.path.exists(image_data):
                with open(image_data, "rb") as f:
                    image_bytes = f.read()
            else:
                if "," in image_data:
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)

            # 👇 A MÁGICA AQUI: Passamos o ID real do usuário em vez de "agent_request"
            result, status = run_xray_pipeline(image_bytes, current_user_id)
            return f"RESULTADO DA ANÁLISE DA CNN DE RAIO-X: {result}"

        except Exception as e:
            print(f"[DEBUG TOOL] ERRO CRÍTICO RAIO-X: {e}")
            return f"Erro ao processar a imagem de Raio-X: {str(e)}"

    return "Aviso: A imagem de Raio-X não foi fornecida."