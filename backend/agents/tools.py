import json
from flask_jwt_extended import get_jwt_identity # <--- O SEGREDO
from langchain_core.tools import tool
from backend.services.ai_service import run_arbovirus_pipeline, run_glaucoma_pipeline

@tool("arbovirus_specialist")
def arbovirus_tool(symptoms: str, age: int, sex: str):
    """
    Use esta ferramenta APENAS quando tiver sintomas claros, idade e sexo do paciente.
    Retorna diagnóstico e hash da blockchain.
    """
    try:
        # Pega o ID do usuário logado via JWT (Automático pelo Flask)
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return {"error": "Usuário não autenticado. Faça login novamente."}

        # Chama o Pipeline Real
        result, status = run_arbovirus_pipeline(symptoms, age, sex, user_id=current_user_id)

        if status != 200:
            return {"error": f"Falha interna no pipeline (Status {status})."}

        # Formata a resposta para o Agente entender e falar bonito
        if isinstance(result, list) and len(result) > 0:
            data = result[0]
            texto = data.get('text', 'Sem texto')
            signature = data.get('extras', {}).get('signature', 'N/A')
            
            return f"""
            [SISTEMA MÉDICO]
            Diagnóstico: {texto}
            Assinatura Blockchain: {signature}
            """
            
        return str(result)

    except Exception as e:
        return {"error": f"Erro crítico na ferramenta: {str(e)}"}

# Mocks para as outras (por enquanto)
@tool("glaucoma_specialist")
def glaucoma_tool(image_path: str = None): 
    """Analisa imagens de fundo de olho."""
    return "Módulo VLM offline."

@tool("lab_manager")
def lab_manager_tool(command: str): 
    """Gerencia treinamentos."""
    return "Lab offline."

MEDICAL_TOOLS = [arbovirus_tool, glaucoma_tool, lab_manager_tool]