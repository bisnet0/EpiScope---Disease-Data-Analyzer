from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.modules.profile.services.profile_service import (
    get_user_profile_service,
    update_user_profile_service
)

def get_profile():
    current_user_id = get_jwt_identity()
    result, status = get_user_profile_service(current_user_id)
    return jsonify(result), status

def update_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400

    result, status = update_user_profile_service(current_user_id, data)
    return jsonify(result), status