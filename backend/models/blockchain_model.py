from datetime import datetime
import uuid
from backend.models.user_model import db


class BlockchainLedger(db.Model):
    __tablename__ = "blockchain_ledger"
    id = db.Column(db.Integer, primary_key=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey("diagnoses.id"), nullable=False)
    payload_hash = db.Column(db.String(66), nullable=False)
    cartesi_index = db.Column(db.Integer)
    transaction_hash = db.Column(db.String(66))
    status = db.Column(db.String(20), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
