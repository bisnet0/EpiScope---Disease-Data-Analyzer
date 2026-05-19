from datetime import datetime
from typing import Any, Dict, Optional

# 👇 Importando o 'db' da nova casa do user_model
from backend.modules.auth.models.user_model import db

class GlaucomaDiagnosis(db.Model): # type: ignore
    __tablename__ = "glaucoma_history"

    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)
    user_email: Any = db.Column(db.String(120), nullable=False)
    username: Any = db.Column(db.String(80), nullable=False)

    image_filename: Any = db.Column(db.String(255), nullable=True)

    prediction_result: Any = db.Column(db.JSON, nullable=False)
    predicted_class: Any = db.Column(db.String(50), nullable=False)
    confidence: Any = db.Column(db.Float, nullable=False)
    model_version: Any = db.Column(db.String(50), default="MobileNetV2_FineTuned")
    blockchain_hash: Any = db.Column(db.String(100), nullable=True)

    # 👇 O construtor explícito que acalma o coração do Pylance!
    def __init__(
        self,
        user_id: str,
        user_email: str,
        username: str,
        prediction_result: dict,
        predicted_class: str,
        confidence: float,
        image_filename: Optional[str] = None,
        model_version: str = "MobileNetV2_FineTuned",
        blockchain_hash: Optional[str] = None,
        created_at: Optional[datetime] = None,
        **kwargs: Any
    ):
        self.user_id = user_id
        self.user_email = user_email
        self.username = username
        self.prediction_result = prediction_result
        self.predicted_class = predicted_class
        self.confidence = confidence
        self.image_filename = image_filename
        self.model_version = model_version
        self.blockchain_hash = blockchain_hash
        
        # Só atribuímos se vier algo, senão o SQLAlchemy cuida do default=datetime.utcnow
        if created_at is not None:
            self.created_at = created_at
            
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.created_at.isoformat() if self.created_at else None,
            "diagnosis": str(self.predicted_class),
            "confidence": float(self.confidence),
            "signature": str(self.blockchain_hash) if self.blockchain_hash else None
        }