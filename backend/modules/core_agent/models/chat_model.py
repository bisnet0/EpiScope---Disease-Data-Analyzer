from datetime import datetime
import uuid
from typing import Any, Dict

# 👇 Importando o 'db' da nova casa do user_model (Módulo de Auth)
from backend.modules.auth.models.user_model import db

class ChatMessage(db.Model): # type: ignore
    __tablename__ = 'chat_messages'
    
    id: Any = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Any = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role: Any = db.Column(db.String(10), nullable=False) # Será 'user' ou 'agent'
    content: Any = db.Column(db.Text, nullable=False)
    has_attachment: Any = db.Column(db.Boolean, default=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)

    # 👇 O construtor explícito que acalma o coração do Pylance!
    def __init__(self, user_id: str, role: str, content: str, has_attachment: bool = False, **kwargs: Any):
        self.user_id = user_id
        self.role = role
        self.content = content
        self.has_attachment = has_attachment
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "role": str(self.role),
            "content": str(self.content),
            "has_attachment": bool(self.has_attachment),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }