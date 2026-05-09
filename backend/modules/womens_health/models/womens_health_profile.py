from backend.modules.auth.models.user_model import db
import uuid
from datetime import datetime
from typing import Any, Dict

class WomensHealthProfile(db.Model): # type: ignore
    __tablename__ = 'womens_health_profiles'

    id: Any = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Any = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Dados Base do Ciclo
    last_period_start: Any = db.Column(db.Date, nullable=True)
    average_cycle_length: Any = db.Column(db.Integer, default=28)
    
    # Flags de Status (Para a IA saber o contexto)
    is_perimenopause: Any = db.Column(db.Boolean, default=False)
    
    updated_at: Any = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 👇 O construtor explícito para o Pylance parar de dar erro!
    def __init__(self, user_id: str, **kwargs: Any):
        self.user_id = user_id
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "last_period_start": self.last_period_start.isoformat() if self.last_period_start else None,
            "average_cycle_length": self.average_cycle_length,
            "is_perimenopause": self.is_perimenopause,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }