from backend.modules.auth.models.user_model import db
from backend.modules.profile.models.profile_model import UserProfile
from datetime import datetime

def get_or_create_profile(user_id: str):
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile

def update_user_profile_service(user_id: str, data: dict):
    try:
        profile = get_or_create_profile(user_id)
        
        if "full_name" in data:
            profile.full_name = data["full_name"]
        if "biological_sex" in data:
            profile.biological_sex = data["biological_sex"]
        if "blood_type" in data:
            profile.blood_type = data["blood_type"]
        if "birth_date" in data and data["birth_date"]:
            # Converte string YYYY-MM-DD para objeto Date
            profile.birth_date = datetime.strptime(data["birth_date"], "%Y-%m-%d").date()

        db.session.commit()
        return {"message": "Perfil atualizado com sucesso", "profile": profile.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro ao atualizar perfil: {str(e)}"}, 500

def get_user_profile_service(user_id: str):
    profile = get_or_create_profile(user_id)
    return {"profile": profile.to_dict()}, 200