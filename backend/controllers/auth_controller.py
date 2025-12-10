from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.services.auth_service import register_user_service, login_user_service, get_user_by_id

def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Faltando dados"}), 400

    result, status = register_user_service(username, email, password)
    return jsonify(result), status

def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not all([email, password]):
        return jsonify({"error": "Faltando credenciais"}), 400

    result, status = login_user_service(email, password)
    return jsonify(result), status

def get_current_user_info():
    current_user_id = get_jwt_identity()
    result, status = get_user_by_id(current_user_id)
    return jsonify(result), status