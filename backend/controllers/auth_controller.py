# backend/controllers/auth_controller.py
from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from backend.models.user_model import db, User

def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Faltando dados"}), 400

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"error": "Usuário já cadastrado"}), 409

    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Criado com sucesso!", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if user and user.check_password(data.get("password")):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"message": "Login OK", "access_token": access_token, "user": user.to_dict()}), 200
    return jsonify({"error": "Credenciais inválidas"}), 401

def get_current_user_info():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    return jsonify(user.to_dict()), 200