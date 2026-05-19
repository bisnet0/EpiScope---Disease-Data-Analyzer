# backend/modules/arbovirus/agents/arbovirus_tools.py

from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain.tools import tool

# 👇 Atenção: O import do ai_service também vai mudar de lugar no futuro,
# mas por enquanto mantemos o caminho antigo até refatorarmos o ai_service.py
from backend.modules.arbovirus.services.arbovirus_service import run_arbovirus_pipeline


def get_safe_user_id():
    """Busca o usuário do Token (se API) ou o primeiro do banco (se Terminal)"""
    if has_request_context():
        try:
            return get_jwt_identity()
        except:
            pass

    from backend.modules.auth.models.user_model import User

    admin = User.query.first()
    return admin.id if admin else None


@tool("arbovirus_specialist")
def arbovirus_tool(symptoms: str, age: int, sex: str):
    """
    Use esta ferramenta APENAS quando tiver sintomas claros, idade e sexo do paciente.
    Retorna diagnóstico de Arboviroses (Dengue, Zika, Chikungunya) e hash da blockchain.
    """
    try:
        current_user_id = get_safe_user_id()

        if not current_user_id:
            return {"error": "Usuário não autenticado. Faça login novamente."}

        result, status = run_arbovirus_pipeline(
            symptoms, age, sex, user_id=current_user_id
        )

        if status != 200:
            return {"error": f"Falha interna no pipeline (Status {status})."}

        if isinstance(result, list) and len(result) > 0:
            data = result[0]
            texto = data.get("text", "Sem texto")
            signature = data.get("extras", {}).get("signature", "N/A")

            return f"""
            [SISTEMA MÉDICO]
            Diagnóstico: {texto}
            Assinatura Blockchain: {signature}
            """

        return str(result)

    except Exception as e:
        return {"error": f"Erro crítico na ferramenta de Arbovírus: {str(e)}"}
