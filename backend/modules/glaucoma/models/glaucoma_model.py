from datetime import datetime
from backend.models.user_model import db

class GlaucomaDiagnosis(db.Model):
    __tablename__ = "glaucoma_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False)

    image_filename = db.Column(db.String(255), nullable=True)

    prediction_result = db.Column(db.JSON, nullable=False)
    predicted_class = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(50), default="MobileNetV2_FineTuned")
    blockchain_hash = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "diagnosis": self.predicted_class,
            "confidence": self.confidence,
            "signature": self.blockchain_hash
        }