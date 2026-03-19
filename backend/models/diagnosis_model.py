from datetime import datetime
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

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "diagnosis": self.top_diagnosis,
            "details": self.prediction_result,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "diagnosis": self.predicted_class,
            "confidence": self.confidence,
        }


class XRayDiagnosis(db.Model):
    __tablename__ = "xray_diagnosis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    image_hash = db.Column(db.String(64), nullable=False)
    prediction_result = db.Column(db.String(50), nullable=False)
    probabilities = db.Column(db.JSON, nullable=False)
    blockchain_hash = db.Column(
        db.String(100), nullable=True
    )  # Para a Cartesi no futuro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "prediction": self.prediction_result,
            "probabilities": self.probabilities,
            "blockchain_hash": self.blockchain_hash,
            "date": self.created_at.isoformat(),
        }
