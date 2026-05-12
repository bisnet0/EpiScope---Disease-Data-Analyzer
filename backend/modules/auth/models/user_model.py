from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from typing import Any, Dict

db: SQLAlchemy = SQLAlchemy()

class User(db.Model):  # type: ignore
    __tablename__ = "users"

    id: Any = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Any = db.Column(db.String(80), unique=True, nullable=False)
    email: Any = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: Any = db.Column(db.String(256), nullable=False)
    
    # 👇 Nova coluna de permissões (Padrão: user)
    role: Any = db.Column(db.String(20), default="user", nullable=False) 
    
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)
    hide_surgery_warning: Any = db.Column(db.Boolean, default=False)

    def __init__(self, username: str, email: str, role: str = "user", **kwargs: Any):
        self.username = username
        self.email = email
        self.role = role
        super().__init__(**kwargs)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "username": str(self.username),
            "email": str(self.email),
            "role": str(self.role), # Retornamos a role para o front-end saber o que renderizar
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }