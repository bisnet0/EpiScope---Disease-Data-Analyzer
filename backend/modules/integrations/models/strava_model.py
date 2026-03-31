from datetime import datetime
from typing import Any, Dict, Optional

# 👇 Importando o 'db' da nova casa do user_model
from backend.modules.auth.models.user_model import db

class StravaCredentials(db.Model): # type: ignore
    __tablename__ = "strava_credentials"

    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.String(50), nullable=False, unique=True)

    access_token: Any = db.Column(db.String(255), nullable=False)
    refresh_token: Any = db.Column(db.String(255), nullable=False)
    expires_at: Any = db.Column(db.Integer, nullable=False)

    created_at: Any = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at: Any = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 👇 Construtor explícito para as credenciais
    def __init__(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: int,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs: Any
    ):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at
            
        super().__init__(**kwargs)


class StravaActivity(db.Model): # type: ignore
    __tablename__ = "strava_activities"

    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.String(50), nullable=False)

    strava_activity_id: Any = db.Column(db.String(50), nullable=False, unique=True)

    name: Any = db.Column(db.String(255))
    activity_type: Any = db.Column(db.String(50))

    distance_meters: Any = db.Column(db.Float)
    moving_time_seconds: Any = db.Column(db.Integer)
    average_heartrate: Any = db.Column(db.Float, nullable=True)
    max_heartrate: Any = db.Column(db.Float, nullable=True)

    start_date: Any = db.Column(db.DateTime)

    average_watts: Any = db.Column(db.Float, nullable=True)
    max_watts: Any = db.Column(db.Float, nullable=True)
    average_temp: Any = db.Column(db.Float, nullable=True)
    elev_high: Any = db.Column(db.Float, nullable=True)

    has_heartrate: Any = db.Column(db.Boolean, default=False)

    raw_data: Any = db.Column(db.JSON)

    # 👇 Construtor explícito para as atividades com todas as métricas opcionais
    def __init__(
        self,
        user_id: str,
        strava_activity_id: str,
        name: Optional[str] = None,
        activity_type: Optional[str] = None,
        distance_meters: Optional[float] = None,
        moving_time_seconds: Optional[int] = None,
        average_heartrate: Optional[float] = None,
        max_heartrate: Optional[float] = None,
        start_date: Optional[datetime] = None,
        average_watts: Optional[float] = None,
        max_watts: Optional[float] = None,
        average_temp: Optional[float] = None,
        elev_high: Optional[float] = None,
        has_heartrate: bool = False,
        raw_data: Optional[Any] = None,
        **kwargs: Any
    ):
        self.user_id = user_id
        self.strava_activity_id = strava_activity_id
        self.name = name
        self.activity_type = activity_type
        self.distance_meters = distance_meters
        self.moving_time_seconds = moving_time_seconds
        self.average_heartrate = average_heartrate
        self.max_heartrate = max_heartrate
        self.start_date = start_date
        self.average_watts = average_watts
        self.max_watts = max_watts
        self.average_temp = average_temp
        self.elev_high = elev_high
        self.has_heartrate = has_heartrate
        self.raw_data = raw_data
        super().__init__(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "activity_id": str(self.strava_activity_id),
            "name": str(self.name) if self.name else None,
            "type": str(self.activity_type) if self.activity_type else None,
            # 👇 Cast explícito para garantir matemática segura
            "distance_km": round(float(self.distance_meters) / 1000, 2)
            if self.distance_meters
            else 0,
            "moving_time_min": round(int(self.moving_time_seconds) / 60, 2)
            if self.moving_time_seconds
            else 0,
            "avg_hr": float(self.average_heartrate) if self.average_heartrate else None,
            "max_hr": float(self.max_heartrate) if self.max_heartrate else None,
            "date": self.start_date.isoformat() if self.start_date else None,
        }