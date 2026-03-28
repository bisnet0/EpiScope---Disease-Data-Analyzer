from datetime import datetime
from backend.models.user_model import db

class GoogleFitData(db.Model):
    __tablename__ = "google_fit_data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    steps = db.Column(db.Integer, default=0)
    sleep_minutes = db.Column(db.Integer, default=0)
    resting_hr = db.Column(db.Float, nullable=True)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "date", name="_user_date_uc"),)


class GoogleFitCredentials(db.Model):
    __tablename__ = "google_fit_credentials"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(50), db.ForeignKey("users.id"), nullable=False, unique=True
    )

    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )