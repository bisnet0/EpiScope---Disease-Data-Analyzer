from flask_jwt_extended import create_access_token
from backend.models.user_model import db, User

def register_user_service(username, email, password):
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return {"error": "Usuário ou email já cadastrados"}, 409

    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "Usuário criado!", "user": new_user.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def login_user_service(email, password):
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return {
            "message": "Login realizado",
            "access_token": access_token,
            "user": user.to_dict()
        }, 200
    
    return {"error": "Credenciais inválidas"}, 401

def get_user_by_id(user_id):
    user = User.query.get(int(user_id))
    if not user:
        return {"error": "Usuário não encontrado"}, 404
    return user.to_dict(), 200