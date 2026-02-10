from langchain_core.tools import tool
# Importe suas funções REAIS da Fase 2
# Se der erro de import aqui, verifique se o caminho backend.services.ai_service está correto
from backend.services.ai_service import run_arbovirus_pipeline, run_glaucoma_pipeline

# --- Ferramenta 1: Especialista em Arboviroses ---
@tool("arbovirus_specialist")
def arbovirus_tool(symptoms: str, age: int, sex: str):
    """
    Use esta ferramenta APENAS quando tiver sintomas claros, idade e sexo do paciente.
    Retorna probabilidades de Dengue, Zika e Chikungunya.
    """
    # Passamos user_id=None pois no terminal não temos sessão, mas a função aceita
    try:
        result, status = run_arbovirus_pipeline(symptoms, age, sex, user_id=None)
        if status != 200:
            return {"error": "Falha técnica na análise do modelo XGBoost."}
        return result
    except Exception as e:
        return {"error": f"Erro interno ao executar modelo: {str(e)}"}

# --- Ferramenta 2: Especialista em Glaucoma ---
@tool("glaucoma_specialist")
def glaucoma_tool(image_path: str = None):
    """
    Analisa imagens de fundo de olho para detectar glaucoma.
    Por enquanto, pede apenas confirmação de recebimento da imagem.
    """
    return {"info": "Processamento de imagem via Agente preparado. Módulo VLM aguardando ativação."}

# --- Ferramenta 3: Gerente de Laboratório ---
@tool("lab_manager")
def lab_manager_tool(command: str):
    """
    Ferramenta administrativa para gerenciar o treinamento de IA.
    Use quando o usuário pedir para 'otimizar', 'evoluir' ou 'treinar'.
    """
    return {"info": "Acesso ao laboratório genético detectado. Aguardando implementação do Auto-Manager."}

# LISTA EXPORTADA - ESSA É A LINHA QUE ESTÁ FALTANDO NO SEU ARQUIVO
MEDICAL_TOOLS = [arbovirus_tool, glaucoma_tool, lab_manager_tool]