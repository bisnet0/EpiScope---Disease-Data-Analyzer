import os
import requests
from flask import request, jsonify, redirect
from flask_jwt_extended import get_jwt_identity

# 👇 Imports mantidos (lembre-se de atualizar os caminhos depois se refatorar os models)
from backend.models.user_model import db
from backend.services.strava_service import sync_user_activities
from backend.models.health_model import StravaCredentials, StravaActivity

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("STRAVA_REDIRECT_URI")

def sync_strava():
    user_id = get_jwt_identity()
    success = sync_user_activities(user_id)
    if success:
        return jsonify({"message": "Sincronização concluída"}), 200
    return jsonify({"error": "Falha na sincronização"}), 500

def get_strava_activities():
    user_id = get_jwt_identity()
    activities = (
        StravaActivity.query.filter_by(user_id=user_id)
        .order_by(StravaActivity.start_date.desc())
        .limit(10)
        .all()
    )
    return jsonify([a.to_dict() for a in activities]), 200

def strava_login():
    print(f"DEBUG STRAVA - CLIENT_ID: {CLIENT_ID}")
    user_id = get_jwt_identity()

    # Escopo 'activity:read_all' é OBRIGATÓRIO para lermos batimentos e treinos completos
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&"
        f"redirect_uri={REDIRECT_URI}&approval_prompt=force&"
        f"scope=read,activity:read_all&"
        f"state={user_id}"  # <-- Truque Sênior: Enviamos o ID do paciente escondido aqui
    )

    return jsonify({"auth_url": auth_url}), 200

def strava_callback():
    code = request.args.get("code")
    user_id = request.args.get("state")  # Recuperamos o ID do paciente!
    error = request.args.get("error")

    # URL do seu frontend (Dashboard)
    FRONTEND_URL = "http://localhost:5173/dashboard"

    if error or not code or not user_id:
        print(f"[STRAVA] Erro na autorização ou dados ausentes: {error}")
        return redirect(f"{FRONTEND_URL}?strava_error=true")

    # Trocamos o código temporário pelo Token de Acesso permanente
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        token_data = response.json()

        # Salva ou atualiza as chaves no cofre (PostgreSQL)
        try:
            cred = StravaCredentials.query.filter_by(user_id=user_id).first()
            if not cred:
                cred = StravaCredentials(user_id=user_id)
                db.session.add(cred)

            cred.access_token = token_data["access_token"]
            cred.refresh_token = token_data["refresh_token"]
            cred.expires_at = token_data["expires_at"]

            db.session.commit()
            print(f"[STRAVA] ✅ Conta conectada com sucesso para o usuário {user_id}")

            return redirect(f"{FRONTEND_URL}?strava_success=true")
        except Exception as e:
            db.session.rollback()
            print(f"[DB ERROR] Erro ao salvar credenciais do Strava: {e}")
            return redirect(f"{FRONTEND_URL}?strava_error=db_fail")
    else:
        print(f"[STRAVA] Falha ao trocar token: {response.text}")
        return redirect(f"{FRONTEND_URL}?strava_error=exchange_fail")

def strava_status():
    user_id = get_jwt_identity()
    cred = StravaCredentials.query.filter_by(user_id=user_id).first()

    if cred and cred.access_token:
        return jsonify({"connected": True}), 200

    return jsonify({"connected": False}), 200