import os
import time
import requests
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user_model import db
from backend.services.google_fit_service import get_google_fit_data
from backend.models.health_model import GoogleFitData, GoogleFitCredentials

google_fit_bp = Blueprint("google_fit", __name__)

CLIENT_ID = os.environ.get("GOOGLE_FIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_FIT_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("GOOGLE_FIT_REDIRECT_URI")


@google_fit_bp.route("/login", methods=["GET"])
@jwt_required()
def google_fit_login():
    user_id = get_jwt_identity()

    scopes = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
    ]

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&response_type=code&"
        f"redirect_uri={REDIRECT_URI}&scope={' '.join(scopes)}&"
        f"access_type=offline&prompt=consent&state={user_id}"
    )

    return jsonify({"auth_url": auth_url}), 200


@google_fit_bp.route("/callback", methods=["GET"])
def google_fit_callback():
    code = request.args.get("code")
    user_id = request.args.get("state")

    if not code:
        return redirect("http://localhost:5173/dashboard/bem-estar?google_error=true")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    res = requests.post(token_url, data=data)

    if res.status_code == 200:
        token_data = res.json()

        expires_at = int(time.time()) + token_data.get("expires_in", 3600)

        creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()
        if not creds:
            creds = GoogleFitCredentials(user_id=user_id)
            db.session.add(creds)

        creds.access_token = token_data.get("access_token")

        new_refresh = token_data.get("refresh_token")
        if new_refresh:
            creds.refresh_token = new_refresh

        creds.expires_at = expires_at

        try:
            db.session.commit()
            print(f"✅ Google Fit token salvo com sucesso para o usuário {user_id}")
            return redirect(
                "http://localhost:5173/dashboard/bem-estar?google_success=true"
            )
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar tokens do Google Fit: {e}")
            return redirect(
                "http://localhost:5173/dashboard/bem-estar?google_error=db_save"
            )

    return redirect(
        "http://localhost:5173/dashboard/bem-estar?google_error=token_exchange_fail"
    )


@google_fit_bp.route("/status", methods=["GET"])
@jwt_required()
def google_fit_status():
    user_id = get_jwt_identity()
    creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()
    return jsonify({"connected": creds is not None}), 200


@google_fit_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_google_data():
    user_id = get_jwt_identity()
    creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()

    if not creds:
        return jsonify({"error": "Google Fit não conectado"}), 404

    # TODO: Implementar refresh_token logic aqui se o token expirar

    metrics = get_google_fit_data(creds.access_token)

    if metrics:
        today = datetime.now().date()
        # Upsert no banco
        entry = GoogleFitData.query.filter_by(user_id=user_id, date=today).first()
        if not entry:
            entry = GoogleFitData(user_id=user_id, date=today)
            db.session.add(entry)

        entry.steps = metrics["steps"]
        entry.sleep_minutes = metrics["sleep_minutes"]
        entry.resting_hr = metrics["resting_hr"]
        entry.last_sync = datetime.utcnow()

        db.session.commit()
        return jsonify({"message": "Sincronizado", "data": metrics}), 200

    return jsonify({"error": "Falha ao obter dados"}), 500


@google_fit_bp.route("/metrics", methods=["GET"])
@jwt_required()
def get_metrics():
    user_id = get_jwt_identity()
    today = datetime.now().date()

    # Busca o registro de hoje no banco
    data = GoogleFitData.query.filter_by(user_id=user_id, date=today).first()

    if data:
        return jsonify(
            {
                "steps": data.steps,
                "sleep_minutes": data.sleep_minutes,
                "resting_hr": data.resting_hr,
                "bpm_min": data.resting_hr,  # Usando o repouso como min por enquanto
            }
        ), 200

    # Se não tiver dados de hoje, retorna zerado para não quebrar o front
    return jsonify({"steps": 0, "sleep_minutes": 0, "resting_hr": 0, "bpm_min": 0}), 200
