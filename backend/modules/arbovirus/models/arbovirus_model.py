from datetime import datetime
# 👇 Import da instância central do SQLAlchemy
from backend.models.user_model import db

class ArbovirusDiagnosis(db.Model):
    __tablename__ = "arbovirus_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    text_description = db.Column(db.Text, nullable=True)

    structured_symptoms = db.Column(db.JSON, nullable=True)
    input_features = db.Column(db.JSON, nullable=True)

    prediction_result = db.Column(db.JSON, nullable=False)
    top_diagnosis = db.Column(db.String(50), nullable=False)
    model_version = db.Column(db.String(50), default="XGBoost_v5")
    blockchain_hash = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "diagnosis": self.top_diagnosis,
            "details": self.prediction_result,
            "signature": self.blockchain_hash
        }