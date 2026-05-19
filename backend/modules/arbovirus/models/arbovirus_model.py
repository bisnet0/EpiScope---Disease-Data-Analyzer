from datetime import datetime
from typing import Any, Dict, Optional
from backend.modules.auth.models.user_model import db

class ArbovirusDiagnosis(db.Model): # type: ignore
    __tablename__ = "arbovirus_history"

    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)
    user_email: Any = db.Column(db.String(120), nullable=False)
    username: Any = db.Column(db.String(80), nullable=False)

    age: Any = db.Column(db.Integer, nullable=False)
    sex: Any = db.Column(db.String(10), nullable=False)
    text_description: Any = db.Column(db.Text, nullable=True)

    structured_symptoms: Any = db.Column(db.JSON, nullable=True)
    input_features: Any = db.Column(db.JSON, nullable=True)

    prediction_result: Any = db.Column(db.JSON, nullable=False)
    top_diagnosis: Any = db.Column(db.String(50), nullable=False)
    model_version: Any = db.Column(db.String(50), default="XGBoost_v5")
    blockchain_hash: Any = db.Column(db.String(100), nullable=True)

    # 👇 O construtor explícito para o VS Code / Pylance parar de reclamar lá no service!
    def __init__(
        self,
        user_id: str,
        user_email: str,
        username: str,
        age: int,
        sex: str,
        text_description: Optional[str],
        structured_symptoms: Optional[dict],
        input_features: Optional[dict],
        prediction_result: dict,
        top_diagnosis: str,
        model_version: str,
        **kwargs: Any
    ):
        self.user_id = user_id
        self.user_email = user_email
        self.username = username
        self.age = age
        self.sex = sex
        self.text_description = text_description
        self.structured_symptoms = structured_symptoms
        self.input_features = input_features
        self.prediction_result = prediction_result
        self.top_diagnosis = top_diagnosis
        self.model_version = model_version
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.created_at.isoformat() if self.created_at else None,
            "diagnosis": str(self.top_diagnosis),
            "details": self.prediction_result,
            "signature": str(self.blockchain_hash) if self.blockchain_hash else None
        }