from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

# 👇 Imports temporários apontando para o ai_service raiz
from backend.modules.laboratory.services.laboratory_service import (
    run_experiment_pipeline,
    get_best_optimization_suggestion,
)


def run_experiment():
    """
    Executa um experimento de treinamento de modelo com hiperparâmetros específicos.
    Usado para testar variações de XGBoost, Random Forest, etc.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    model_type = data.get("model_type")
    params = data.get("params")

    if not model_type or not params:
        return jsonify({"error": "Parâmetros ou tipo de modelo faltando"}), 400

    result, status = run_experiment_pipeline(current_user_id, model_type, params)
    return jsonify(result), status


def get_ai_suggestion():
    """
    Consulta o histórico de experimentos genéticos e retorna a melhor sugestão 
    de otimização encontrada até o momento pelo laboratório autônomo.
    """
    result, status = get_best_optimization_suggestion()
    return jsonify(result), status