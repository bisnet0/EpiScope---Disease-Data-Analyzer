from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain.tools import tool

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

        # 👇 Imports temporários apontando para o ai_service antigo
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