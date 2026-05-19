from datetime import datetime
from typing import Any, Dict, Optional
import uuid

# 👇 Importando o 'db' do núcleo de autenticação
from backend.modules.auth.models.user_model import db

class WomensHealthAnalysis(db.Model): # type: ignore
    __tablename__ = 'womens_health_analysis'

    # Definição das Colunas com Any para silenciar o Pylance nas atribuições
    id: Any = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Any = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    exam_type: Any = db.Column(db.String(20), nullable=False)  # 'AUDIO' ou 'VIDEO'
    consultation_type: Any = db.Column(db.String(50))         # 'TRIAGEM_VIOLENCIA', etc.
    
    dominant_result: Any = db.Column(db.String(50))           # Ex: 'ALERTA: Pavor'
    raw_data: Any = db.Column(db.JSON)                        # O espectro emocional
    transcription: Any = db.Column(db.Text, nullable=True)
    
    confidence_score: Any = db.Column(db.Float, default=0.0)
    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)

    # 👇 O construtor explícito que mantém o padrão do projeto
    def __init__(
        self,
        exam_type: str,
        dominant_result: str,
        raw_data: Dict[str, Any],
        consultation_type: Optional[str] = "GINECOLOGICA",
        patient_id: Optional[int] = None,
        transcription: Optional[str] = None,
        confidence_score: float = 0.0,
        created_at: Optional[datetime] = None,
        **kwargs: Any
    ):
        self.exam_type = exam_type
        self.dominant_result = dominant_result
        self.raw_data = raw_data
        self.consultation_type = consultation_type
        self.patient_id = patient_id
        self.transcription = transcription
        self.confidence_score = confidence_score
        
        if created_at is not None:
            self.created_at = created_at
            
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "exam_type": str(self.exam_type),
            "consultation_type": str(self.consultation_type),
            "dominant_result": str(self.dominant_result),
            "raw_data": self.raw_data,
            "transcription": self.transcription,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }