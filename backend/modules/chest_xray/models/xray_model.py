from datetime import datetime
from backend.models.user_model import db

class XRayDiagnosis(db.Model):
    __tablename__ = "xray_diagnosis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    image_hash = db.Column(db.String(64), nullable=False)
    prediction_result = db.Column(db.String(50), nullable=False)
    probabilities = db.Column(db.JSON, nullable=False)
    blockchain_hash = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "prediction": self.prediction_result,
            "probabilities": self.probabilities,
            "date": self.created_at.isoformat(),
            "signature": self.blockchain_hash
        }