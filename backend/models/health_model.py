from datetime import datetime
from backend.models.user_model import db

class StravaCredentials(db.Model):
    __tablename__ = "strava_credentials"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    
    # Tokens OAuth 2.0
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False) # Unix Timestamp de expiração
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StravaActivity(db.Model):
    __tablename__ = "strava_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    
    # ID único da corrida lá no Strava para não duplicarmos dados
    strava_activity_id = db.Column(db.String(50), nullable=False, unique=True) 
    
    name = db.Column(db.String(255))
    activity_type = db.Column(db.String(50)) # Ex: "Run", "Ride", "Swim"
    
    # Métricas Fisiológicas e Físicas
    distance_meters = db.Column(db.Float)
    moving_time_seconds = db.Column(db.Integer)
    average_heartrate = db.Column(db.Float, nullable=True) # BPM
    max_heartrate = db.Column(db.Float, nullable=True)     # BPM
    
    start_date = db.Column(db.DateTime)
    
    average_watts = db.Column(db.Float, nullable=True)
    max_watts = db.Column(db.Float, nullable=True)
    average_temp = db.Column(db.Float, nullable=True)
    elev_high = db.Column(db.Float, nullable=True) # Altimetria máxima
    
    # Campo para identificar se houve uso de sensor cardíaco
    has_heartrate = db.Column(db.Boolean, default=False)
    
    # Guardamos o JSON bruto caso o Agente de IA precise de algo ultra específico no futuro (ex: altimetria)
    raw_data = db.Column(db.JSON) 
    
    def to_dict(self):
        return {
            "id": self.id,
            "activity_id": self.strava_activity_id,
            "name": self.name,
            "type": self.activity_type,
            "distance_km": round(self.distance_meters / 1000, 2) if self.distance_meters else 0,
            "moving_time_min": round(self.moving_time_seconds / 60, 2) if self.moving_time_seconds else 0,
            "avg_hr": self.average_heartrate,
            "max_hr": self.max_heartrate,
            "date": self.start_date.isoformat() if self.start_date else None
        }