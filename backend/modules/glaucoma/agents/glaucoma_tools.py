import os
import base64
from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain.tools import tool

# 👇 O import do ai_service temporário até a refatoração total
from backend.services.ai_service import run_glaucoma_pipeline

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


@tool("glaucoma_specialist")
def glaucoma_tool(image_data: str):
    """
    Analisa imagens de fundo de olho para detectar glaucoma.
    A entrada 'image_data' pode ser um caminho local ou uma string base64.
    """
    print("\n[DEBUG TOOL] Iniciando análise Híbrida de Glaucoma...")
    try:
        current_user_id = get_safe_user_id()
        if not current_user_id:
            return {"error": "Nenhum usuário encontrado no sistema."}

        if os.path.exists(image_data):
            with open(image_data, "rb") as f:
                image_bytes = f.read()
        else:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)

        result, status = run_glaucoma_pipeline(image_bytes, user_id=current_user_id)

        print(f"[DEBUG TOOL] Status Glaucoma: {status}")

        if status != 200:
            return {"error": f"Falha na análise visual (Status {status})."}

        laudo = result.get("friendly_response", "Laudo não gerado.")
        probs = result.get("analysis_details", {}).get("probabilities", {})

        return f"""
        [SISTEMA DE VISÃO ATIVADO]
        Confiança Matemática da CNN: {probs}
        
        Parecer Clínico do Oftalmologista IA (VLM):
        {laudo}
        """

    except Exception as e:
        print(f"[DEBUG TOOL] ERRO CRÍTICO VISÃO: {e}")
        return {"error": str(e)}