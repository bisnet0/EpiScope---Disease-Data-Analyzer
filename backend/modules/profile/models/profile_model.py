from backend.modules.auth.models.user_model import db
from datetime import datetime
from typing import Any, Dict

class UserProfile(db.Model): # type: ignore
    __tablename__ = "user_profiles"

    id: Any = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Any = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    
    full_name: Any = db.Column(db.String(150), nullable=True)
    birth_date: Any = db.Column(db.Date, nullable=True)
    biological_sex: Any = db.Column(db.String(20), nullable=True)
    blood_type: Any = db.Column(db.String(5), nullable=True)
    
    updated_at: Any = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 👇 ADICIONE ESTE BLOCO PARA O PYLANCE RECONHECER OS PARÂMETROS
    def __init__(self, user_id: str, **kwargs: Any):
        self.user_id = user_id
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_name": self.full_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "biological_sex": self.biological_sex,
            "blood_type": self.blood_type,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }