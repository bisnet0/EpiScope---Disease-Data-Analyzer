from datetime import datetime

# 👇 Importando o 'db' da nova casa do user_model
from backend.modules.auth.models.user_model import db

class ModelTrainingLog(db.Model):
    __tablename__ = "model_training_logs"

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    model_name = db.Column(db.String(50), nullable=False)
    version = db.Column(db.String(20), nullable=False)

    parameters = db.Column(db.JSON, nullable=True)
    feature_importance = db.Column(db.JSON, nullable=True)

    metrics = db.Column(db.JSON, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)

    dataset_size = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "model": f"{self.model_name} ({self.version})",
            "accuracy": self.accuracy,
        }