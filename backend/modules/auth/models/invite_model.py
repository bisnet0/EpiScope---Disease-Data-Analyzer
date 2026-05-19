import secrets
import string
from datetime import datetime, timedelta
from backend.modules.auth.models.user_model import db, Any, Dict

class InviteCode(db.Model): # type: ignore
    __tablename__ = "invite_codes"

    id: Any = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code: Any = db.Column(db.String(20), unique=True, nullable=False)
    created_by: Any = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    is_used: Any = db.Column(db.Boolean, default=False)
    expires_at: Any = db.Column(db.DateTime, nullable=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, created_by: str, days_valid: int = 7):
        self.code = self.generate_secure_code()
        self.created_by = created_by
        self.expires_at = datetime.utcnow() + timedelta(days=days_valid)

    @staticmethod
    def generate_secure_code(length: int = 8) -> str:
        # Gera algo como EPI-X8J2-9A1
        alphabet = string.ascii_uppercase + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
        return f"EPI-{random_part}"

    def is_valid(self) -> bool:
        return not self.is_used and datetime.utcnow() < self.expires_at