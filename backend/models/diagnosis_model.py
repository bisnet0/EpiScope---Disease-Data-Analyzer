from datetime import datetime
from backend.models.user_model import db

class ArbovirusDiagnosis(db.Model):
    __tablename__ = 'arbovirus_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dados de Entrada (Log do que o usuário enviou)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    text_description = db.Column(db.Text, nullable=True)
    
    # Dados Processados (Log do que a IA entendeu)
    structured_symptoms = db.Column(db.JSON, nullable=True) # Sintomas extraídos pelo Gemini
    input_features = db.Column(db.JSON, nullable=True)      # Vetor usado no XGBoost
    
    # Resultados (Log da Avaliação do Modelo)
    prediction_result = db.Column(db.JSON, nullable=False)  # Probabilidades completas
    top_diagnosis = db.Column(db.String(50), nullable=False)
    model_version = db.Column(db.String(50), default="XGBoost_v5") # Útil para comparar versões depois

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "diagnosis": self.top_diagnosis,
            "details": self.prediction_result
        }

class GlaucomaDiagnosis(db.Model):
    __tablename__ = 'glaucoma_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadados da Imagem
    image_filename = db.Column(db.String(255), nullable=True) # Caso salvemos o arquivo no futuro
    
    # Resultados
    prediction_result = db.Column(db.JSON, nullable=False) # Probabilidades
    predicted_class = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(50), default="MobileNetV2_FineTuned")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "diagnosis": self.predicted_class,
            "confidence": self.confidence
        }