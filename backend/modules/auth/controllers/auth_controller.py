from flask import request, jsonify
from flask_jwt_extended import (
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
import os

# 👇 Imports mantidos (apontando para o auth_service)
from backend.modules.auth.services.auth_service import (
    register_user_service,
    login_user_service,
    get_user_by_id,
    refresh_token_service,
    update_user_preferences_service,
)

def update_user_preferences():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400

    result, status = update_user_preferences_service(current_user_id, data)
    return jsonify(result), status


def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    # 👇 A barreira da Master Key
    master_key = data.get("master_key")
    expected_key = os.environ.get("MASTER_REGISTER_KEY")
    
    if not master_key or master_key != expected_key:
        return jsonify({"error": "Acesso negado: Chave Mestra inválida ou ausente."}), 403

    if not all([username, email, password]):
        return jsonify({"error": "Faltando dados"}), 400

    # Dica: Lá no seu auth_service.py, você pode passar a role baseada na master_key se quiser ter uma MASTER_KEY_ADMIN separada depois.
    result, status = register_user_service(username, email, password)

    if status == 201:
        resp = jsonify({"message": result["message"], "user": result["user"]})
        set_access_cookies(resp, result["access_token"])
        set_refresh_cookies(resp, result["refresh_token"])
        return resp, status

    return jsonify(result), status


def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Faltando credenciais"}), 400

    result, status = login_user_service(email, password)

    if status == 200:
        resp = jsonify({"message": result["message"], "user": result["user"]})
        set_access_cookies(resp, result["access_token"])
        set_refresh_cookies(resp, result["refresh_token"])
        return resp, status

    return jsonify(result), status


def logout_user():
    resp = jsonify({"message": "Logout realizado com sucesso"})
    unset_jwt_cookies(resp)
    return resp, 200


def refresh_access_token():
    current_user_id = get_jwt_identity()

    result, status = refresh_token_service(current_user_id)

    if status == 200:
        resp = jsonify({"message": "Token renovado"})
        set_access_cookies(resp, result["access_token"])
        return resp, status

    return jsonify(result), status


def get_current_user_info():
    current_user_id = get_jwt_identity()
    result, status = get_user_by_id(current_user_id)
    return jsonify(result), status