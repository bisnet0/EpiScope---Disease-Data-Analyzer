from datetime import datetime
from typing import Any, Dict
from backend.modules.auth.models.user_model import db

class XRayDiagnosis(db.Model): # type: ignore
    __tablename__ = "xray_diagnosis"

    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.String(50), nullable=False)
    image_hash: Any = db.Column(db.String(64), nullable=False)
    prediction_result: Any = db.Column(db.String(50), nullable=False)
    probabilities: Any = db.Column(db.JSON, nullable=False)
    blockchain_hash: Any = db.Column(db.String(100), nullable=True)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)

    # 👇 O construtor explícito para o VS Code / Pylance entender os parâmetros!
    def __init__(self, user_id: str, image_hash: str, prediction_result: str, probabilities: dict, **kwargs: Any):
        self.user_id = user_id
        self.image_hash = image_hash
        self.prediction_result = prediction_result
        self.probabilities = probabilities
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prediction": str(self.prediction_result),
            "probabilities": self.probabilities,
            "date": self.created_at.isoformat() if self.created_at else None,
            "signature": str(self.blockchain_hash) if self.blockchain_hash else None
        }