from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from typing import Any, Dict

db: SQLAlchemy = SQLAlchemy()

class User(db.Model):  # type: ignore
    __tablename__ = 'users'

    id: Any = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Any = db.Column(db.String(80), unique=True, nullable=False)
    email: Any = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: Any = db.Column(db.String(256), nullable=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)

    # 👇 ADICIONE ISTO AQUI! O construtor explícito que o Pylance exige.
    def __init__(self, username: str, email: str, **kwargs: Any):
        self.username = username
        self.email = email
        super().__init__(**kwargs) # Garante que o SQLAlchemy faça a mágica dele com o resto

    def set_password(self, password: str) -> None:
        """Cria o hash da senha para não salvar texto puro"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica se a senha enviada bate com o hash salvo"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "username": str(self.username),
            "email": str(self.email),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }