from datetime import datetime
from typing import Any, Optional, Dict

# 👇 Importando o 'db' da nova casa do user_model
from backend.modules.auth.models.user_model import db

class GoogleFitData(db.Model): # type: ignore
    __tablename__ = "google_fit_data"
    
    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    date: Any = db.Column(db.Date, nullable=False)
    steps: Any = db.Column(db.Integer, default=0)
    sleep_minutes: Any = db.Column(db.Integer, default=0)
    resting_hr: Any = db.Column(db.Float, nullable=True)
    last_sync: Any = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__: Any = (db.UniqueConstraint("user_id", "date", name="_user_date_uc"),)

    # 👇 Construtor explícito para os dados de saúde
    def __init__(
        self,
        user_id: str,
        date: Any, # O SQLAlchemy aceita objeto datetime.date ou string "YYYY-MM-DD"
        steps: int = 0,
        sleep_minutes: int = 0,
        resting_hr: Optional[float] = None,
        last_sync: Optional[datetime] = None,
        **kwargs: Any
    ):
        self.user_id = user_id
        self.date = date
        self.steps = steps
        self.sleep_minutes = sleep_minutes
        self.resting_hr = resting_hr
        
        if last_sync is not None:
            self.last_sync = last_sync
            
        super().__init__(**kwargs)


class GoogleFitCredentials(db.Model): # type: ignore
    __tablename__ = "google_fit_credentials"

    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(
        db.String(50), db.ForeignKey("users.id"), nullable=False, unique=True
    )

    access_token: Any = db.Column(db.Text, nullable=False)
    refresh_token: Any = db.Column(db.Text, nullable=True)
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
        expires_at: int,
        refresh_token: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs: Any
    ):
        self.user_id = user_id
        self.access_token = access_token
        self.expires_at = expires_at
        self.refresh_token = refresh_token
        
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at
            
        super().__init__(**kwargs)