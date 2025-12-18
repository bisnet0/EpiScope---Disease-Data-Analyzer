from datetime import datetime
from backend.models.user_model import db

class ModelTrainingLog(db.Model):
    __tablename__ = 'model_training_logs'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Identificação do Modelo
    model_name = db.Column(db.String(50), nullable=False) # ex: "Arbovirus_XGBoost"
    version = db.Column(db.String(20), nullable=False)    # ex: "v5"
    
    # Metadados de Treino
    parameters = db.Column(db.JSON, nullable=True)        # Hiperparâmetros usados
    feature_importance = db.Column(db.JSON, nullable=True)# Ranking das features
    
    # Métricas de Avaliação
    metrics = db.Column(db.JSON, nullable=False)          # O classification_report completo
    accuracy = db.Column(db.Float, nullable=True)         # Para ordenação rápida
    
    dataset_size = db.Column(db.Integer, nullable=True)   # Quantas linhas foram usadas

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.created_at.isoformat(),
            "model": f"{self.model_name} ({self.version})",
            "accuracy": self.accuracy
        }