from datetime import datetime
from backend.models.user_model import db

class StravaCredentials(db.Model):
    __tablename__ = "strava_credentials"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)

    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class StravaActivity(db.Model):
    __tablename__ = "strava_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)

    strava_activity_id = db.Column(db.String(50), nullable=False, unique=True)

    name = db.Column(db.String(255))
    activity_type = db.Column(db.String(50))

    distance_meters = db.Column(db.Float)
    moving_time_seconds = db.Column(db.Integer)
    average_heartrate = db.Column(db.Float, nullable=True)
    max_heartrate = db.Column(db.Float, nullable=True)

    start_date = db.Column(db.DateTime)

    average_watts = db.Column(db.Float, nullable=True)
    max_watts = db.Column(db.Float, nullable=True)
    average_temp = db.Column(db.Float, nullable=True)
    elev_high = db.Column(db.Float, nullable=True)

    has_heartrate = db.Column(db.Boolean, default=False)

    raw_data = db.Column(db.JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "activity_id": self.strava_activity_id,
            "name": self.name,
            "type": self.activity_type,
            "distance_km": round(self.distance_meters / 1000, 2)
            if self.distance_meters
            else 0,
            "moving_time_min": round(self.moving_time_seconds / 60, 2)
            if self.moving_time_seconds
            else 0,
            "avg_hr": self.average_heartrate,
            "max_hr": self.max_heartrate,
            "date": self.start_date.isoformat() if self.start_date else None,
        }