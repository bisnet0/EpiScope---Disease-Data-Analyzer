from backend.modules.auth.models.user_model import db, User
from backend.modules.auth.models.invite_model import InviteCode

def create_invite_service(admin_id: str):
    # Verifica se quem está criando é admin
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return {"error": "Apenas administradores podem gerar convites."}, 403

    new_invite = InviteCode(created_by=admin_id)
    db.session.add(new_invite)
    db.session.commit()
    return {"code": new_invite.code, "expires_at": new_invite.expires_at.isoformat()}, 201

def validate_and_use_invite(code_str: str) -> bool:
    invite = InviteCode.query.filter_by(code=code_str).first()
    if invite and invite.is_valid():
        invite.is_used = True
        db.session.commit()
        return True
    return False