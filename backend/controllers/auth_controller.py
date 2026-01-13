# backend/controllers/auth_controller.py
from flask import request, jsonify
from flask_jwt_extended import (
    get_jwt_identity, 
    set_access_cookies, 
    set_refresh_cookies, 
    unset_jwt_cookies
)
from backend.services.auth_service import (
    register_user_service, 
    login_user_service, 
    get_user_by_id,
    refresh_token_service
)

def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Faltando dados"}), 400

    result, status = register_user_service(username, email, password)
    
    if status == 201:
        # Se criou com sucesso, setamos os cookies
        resp = jsonify({"message": result['message'], "user": result['user']})
        set_access_cookies(resp, result['access_token'])
        set_refresh_cookies(resp, result['refresh_token'])
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
        # Login OK -> Setar Cookies HttpOnly
        resp = jsonify({"message": result['message'], "user": result['user']})
        set_access_cookies(resp, result['access_token'])
        set_refresh_cookies(resp, result['refresh_token'])
        return resp, status

    return jsonify(result), status

def logout_user():
    # Para deslogar, basta limpar os cookies
    resp = jsonify({"message": "Logout realizado com sucesso"})
    unset_jwt_cookies(resp)
    return resp, 200

def refresh_access_token():
    # O decorator @jwt_required(refresh=True) na rota já validou o cookie de refresh
    current_user_id = get_jwt_identity()
    
    result, status = refresh_token_service(current_user_id)
    
    if status == 200:
        resp = jsonify({"message": "Token renovado"})
        set_access_cookies(resp, result['access_token'])
        return resp, status
        
    return jsonify(result), status

def get_current_user_info():
    # O decorator @jwt_required() vai olhar o cookie access_token_cookie automaticamente
    current_user_id = get_jwt_identity()
    result, status = get_user_by_id(current_user_id)
    return jsonify(result), status