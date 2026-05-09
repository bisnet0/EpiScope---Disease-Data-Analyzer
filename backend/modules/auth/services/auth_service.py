from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)

# 👇 O IMPORT CORRIGIDO APONTANDO PARA A NOVA CASA
from backend.modules.auth.models.user_model import db, User


def register_user_service(username, email, password):
    if (
        User.query.filter_by(email=email).first()
        or User.query.filter_by(username=username).first()
    ):
        return {"error": "Usuário ou email já cadastrados"}, 409

    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))

        return {
            "message": "Usuário criado!",
            "user": new_user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def login_user_service(email, password):
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "message": "Login realizado",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200

    return {"error": "Credenciais inválidas"}, 401


def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "Usuário não encontrado"}, 404
    return user.to_dict(), 200


def refresh_token_service(current_user_id):
    if not current_user_id:
        return {"error": "Token inválido"}, 401

    new_access_token = create_access_token(identity=current_user_id)
    return {"access_token": new_access_token}, 200


def update_user_preferences_service(user_id, preferences_data):
    user = User.query.get(user_id)
    if not user:
        return {"error": "Usuário não encontrado"}, 404

    try:
        if "hide_surgery_warning" in preferences_data:
            user.hide_surgery_warning = bool(preferences_data["hide_surgery_warning"])

        db.session.commit()
        return {
            "message": "Preferências atualizadas com sucesso",
            "user": user.to_dict(),
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro ao salvar preferências: {str(e)}"}, 500
