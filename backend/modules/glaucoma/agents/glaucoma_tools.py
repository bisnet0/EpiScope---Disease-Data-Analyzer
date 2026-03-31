import os
import base64
from typing import Optional, Dict, Any
from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain.tools import tool

# 👇 O import do ai_service temporário até a refatoração total
from backend.modules.glaucoma.services.glaucoma_service import run_glaucoma_pipeline

def get_safe_user_id() -> Optional[str]:
    """Busca o usuário do Token (se API) ou o primeiro do banco (se Terminal)"""
    if has_request_context():
        try:
            identity = get_jwt_identity()
            if identity:
                return str(identity)
        except Exception:
            pass

    from backend.modules.auth.models.user_model import User
    admin = User.query.first() # type: ignore
    return str(admin.id) if admin else None


@tool("glaucoma_specialist")
def glaucoma_tool(image_data: str) -> str:
    """
    Analisa imagens de fundo de olho para detectar glaucoma.
    A entrada 'image_data' pode ser um caminho local ou uma string base64.
    """
    print("\n[DEBUG TOOL] Iniciando análise Híbrida de Glaucoma...")
    try:
        current_user_id = get_safe_user_id()
        if not current_user_id:
            return "Erro: Nenhum usuário autenticado encontrado no sistema."

        if os.path.exists(image_data):
            with open(image_data, "rb") as f:
                image_bytes = f.read()
        else:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)

        # Roda o pipeline (que devolve tupla de result e status)
        result, status = run_glaucoma_pipeline(image_bytes, user_id=current_user_id)

        print(f"[DEBUG TOOL] Status Glaucoma: {status}")

        if status != 200:
            return f"Erro: Falha na análise visual (Status {status})."

        # 👇 TYPE GUARD SALVADOR! Acalma o Pylance dizendo que result É um dicionário
        if isinstance(result, dict):
            laudo = str(result.get("friendly_response", "Laudo não gerado."))
            
            # Type guard aninhado para garantir o acesso seguro em "analysis_details"
            analysis_details = result.get("analysis_details")
            if isinstance(analysis_details, dict):
                probs = analysis_details.get("probabilities", {})
            else:
                probs = {}

            return f"""
            [SISTEMA DE VISÃO ATIVADO]
            Confiança Matemática da CNN: {probs}
            
            Parecer Clínico do Oftalmologista IA (VLM):
            {laudo}
            """
        
        # Fallback caso o pipeline devolva algo muito bizarro (tipo uma string pura)
        return f"Aviso: Análise concluída, mas o formato da resposta é desconhecido: {result}"

    except Exception as e:
        print(f"[DEBUG TOOL] ERRO CRÍTICO VISÃO: {e}")
        return f"Erro Crítico na ferramenta de Glaucoma: {str(e)}"