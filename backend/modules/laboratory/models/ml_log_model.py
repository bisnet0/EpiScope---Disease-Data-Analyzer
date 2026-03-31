from datetime import datetime
from typing import Any, Dict, Optional

# 👇 Importando o 'db' da nova casa do user_model
from backend.modules.auth.models.user_model import db

class ModelTrainingLog(db.Model): # type: ignore
    __tablename__ = "model_training_logs"

    id: Any = db.Column(db.Integer, primary_key=True)
    
    user_id: Any = db.Column(db.String(50), nullable=True)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)

    model_name: Any = db.Column(db.String(50), nullable=False)
    version: Any = db.Column(db.String(20), nullable=False)

    parameters: Any = db.Column(db.JSON, nullable=True)
    feature_importance: Any = db.Column(db.JSON, nullable=True)

    metrics: Any = db.Column(db.JSON, nullable=False)
    accuracy: Any = db.Column(db.Float, nullable=True)

    dataset_size: Any = db.Column(db.Integer, nullable=True)

    # 👇 O construtor explícito que acalma o coração do Pylance!
    def __init__(
        self,
        model_name: str,
        version: str,
        metrics: Any,
        user_id: Optional[str] = None,
        parameters: Optional[Any] = None,
        feature_importance: Optional[Any] = None,
        accuracy: Optional[float] = None,
        dataset_size: Optional[int] = None,
        created_at: Optional[datetime] = None,
        **kwargs: Any
    ):
        self.model_name = model_name
        self.version = version
        self.metrics = metrics
        self.user_id = user_id
        self.parameters = parameters
        self.feature_importance = feature_importance
        self.accuracy = accuracy
        self.dataset_size = dataset_size
        
        # Só atribuímos se vier algo, senão o SQLAlchemy cuida do default=datetime.utcnow
        if created_at is not None:
            self.created_at = created_at
            
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.created_at.isoformat() if self.created_at else None,
            "model": f"{self.model_name} ({self.version})",
            "accuracy": self.accuracy,
        }