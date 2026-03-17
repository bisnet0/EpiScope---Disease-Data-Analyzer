import json
from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain_core.tools import tool
from backend.models.user_model import User
from backend.services.ai_service import run_arbovirus_pipeline, run_glaucoma_pipeline
import os
import base64

from langchain.tools import tool
from backend.services.rag_service import search_knowledge_base


def get_safe_user_id():
    """Busca o usuário do Token (se API) ou o primeiro do banco (se Terminal)"""
    if has_request_context():
        try:
            return get_jwt_identity()
        except:
            pass

    admin = User.query.first()
    return admin.id if admin else None


@tool("arbovirus_specialist")
def arbovirus_tool(symptoms: str, age: int, sex: str):
    """
    Use esta ferramenta APENAS quando tiver sintomas claros, idade e sexo do paciente.
    Retorna diagnóstico e hash da blockchain.
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
        return {"error": f"Erro crítico na ferramenta: {str(e)}"}


@tool("xray_tool")
def xray_tool(image_base64: str = None):
    """
    Usa a Rede Neural Convolucional (CNN) para analisar imagens de Raio-X de Tórax (Chest X-Ray).
    Devolve a probabilidade do paciente ter Pneumonia, Tuberculose ou pulmão Normal.
    USE ESTA FERRAMENTA QUANDO o usuário enviar uma imagem e perguntar se ele tem pneumonia,
    anomalia pulmonar, ou pedir para avaliar um raio-x.
    """
    print("\n[AGENTE] 🩻 Acionando o Radiologista de IA (CNN Raio-X)...")

    from backend.services.ai_service import run_xray_pipeline
    import base64

    if image_base64:
        try:
            image_bytes = base64.b64decode(
                image_base64.split(",")[1] if "," in image_base64 else image_base64
            )

            result, status = run_xray_pipeline(image_bytes, "agent_request")
            return f"RESULTADO DA ANÁLISE DE RAIO-X: {result}"
        except Exception as e:
            return f"Erro ao decodificar a imagem de Raio-X: {str(e)}"

    return "Aviso: A imagem de Raio-X não foi fornecida pelo usuário."


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


@tool("lab_manager")
def lab_manager_tool(
    target_disease: str = "não_informado",
    model_type: str = "xgboost",
    generations: int = 3,
    population_size: int = 5,
):
    """
    Gerencia o laboratório de IA e executa otimizações genéticas (Hyperparameter Tuning).
    Use APENAS quando o usuário pedir explicitamente para otimizar, treinar, evoluir ou melhorar os modelos.
    - target_disease: "arbovirus" ou "glaucoma"
    - model_type: "xgboost", "random_forest", ou "decision_tree"
    - generations: número de gerações (padrão 3 para testes)
    - population_size: tamanho da população (padrão 5)
    Retorna o histórico de otimização e os melhores parâmetros encontrados.
    """

    if target_disease not in ["arbovirus", "glaucoma"]:
        return "INSTRUÇÃO PARA O AGENTE: Você precisa perguntar ao usuário qual doença ele deseja otimizar (Arboviroses ou Glaucoma) antes de prosseguir."

    print(
        f"\n[DEBUG TOOL] Iniciando Laboratório Genético para {target_disease} | Modelo: {model_type}..."
    )
    try:
        current_user_id = get_safe_user_id()
        if not current_user_id:
            return {
                "error": "Nenhum usuário encontrado no sistema para registrar a otimização."
            }

        ga_config = {
            "generations": generations,
            "population_size": population_size,
            "mutation_rate": 0.1,
            "crossover_rate": 0.7,
        }

        if target_disease.lower() == "arbovirus":
            from backend.services.ai_service import run_genetic_pipeline

            result, status = run_genetic_pipeline(
                model_type, current_user_id, ga_config
            )
        elif target_disease.lower() == "glaucoma":
            from backend.services.ai_service import run_glaucoma_genetic_pipeline

            result, status = run_glaucoma_genetic_pipeline(
                model_type, current_user_id, ga_config
            )
        else:
            return "Erro: Doença alvo desconhecida. O sistema só suporta 'arbovirus' ou 'glaucoma'."

        print(f"[DEBUG TOOL] Status Lab: {status}")

        if status != 200:
            return f"Falha na otimização (Status {status}). Detalhes: {result.get('error', 'Desconhecido')}"

        best_acc = result.get("best_individual", {}).get("accuracy", 0) * 100
        best_params = result.get("best_individual", {}).get("params", {})

        return f"""
        [LABORATÓRIO AUTÔNOMO CONCLUÍDO]
        Doença Alvo: {target_disease.upper()}
        Modelo Otimizado: {model_type.upper()}
        Gerações Completadas: {generations}
        Tamanho da População: {population_size}
        
        Nova Acurácia Máxima Atingida: {best_acc:.2f}%
        Melhores Parâmetros Encontrados: {best_params}
        
        Os resultados da otimização foram salvos no banco de dados de logs de ML.
        """

    except Exception as e:
        print(f"[DEBUG TOOL] ERRO CRÍTICO LAB: {e}")
        return {"error": f"Erro fatal na otimização: {str(e)}"}


@tool("rag_clinical_tool")
def rag_clinical_tool(query: str):
    """
    Busca na base de conhecimento (PDFs médicos, protocolos do Ministério da Saúde, artigos científicos).
    USE ESTA FERRAMENTA SEMPRE que o paciente pedir explicações aprofundadas sobre Dengue, Zika, Chikungunya ou Glaucoma,
    ou quando precisar recomendar procedimentos, laudos estruturados e diretrizes clínicas oficiais.
    """
    print(f"\n[AGENTE] 📚 Consultando a biblioteca médica para: '{query}'...")

    resultado_busca = search_knowledge_base(query=query, k=4)

    return f"""
    RESULTADOS DA BUSCA NA LITERATURA CLÍNICA:
    {resultado_busca}
    
    INSTRUÇÃO AO AGENTE: Use os trechos acima para embasar sua resposta. Cite a fonte de forma natural se aplicável.
    """


MEDICAL_TOOLS = [arbovirus_tool, glaucoma_tool, lab_manager_tool, rag_clinical_tool, xray_tool]
