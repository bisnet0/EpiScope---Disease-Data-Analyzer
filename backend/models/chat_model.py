from datetime import datetime
import uuid
from backend.models.user_model import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False) # Será 'user' ou 'agent'
    content = db.Column(db.Text, nullable=False)
    has_attachment = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "has_attachment": self.has_attachment,
            "created_at": self.created_at.isoformat()
        }