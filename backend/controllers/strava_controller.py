import os
import requests
from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user_model import db
from backend.services.strava_service import sync_user_activities
from backend.models.health_model import StravaCredentials, StravaActivity

strava_bp = Blueprint("strava", __name__)

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("STRAVA_REDIRECT_URI")

# 1. Rota que o Frontend chama para iniciar o fluxo


# Rota para forçar a sincronização (Botão de 'Atualizar')
@strava_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_strava():
    user_id = get_jwt_identity()
    success = sync_user_activities(user_id)
    if success:
        return jsonify({"message": "Sincronização concluída"}), 200
    return jsonify({"error": "Falha na sincronização"}), 500


# Rota para o Front listar as atividades e batimentos
@strava_bp.route("/activities", methods=["GET"])
@jwt_required()
def get_strava_activities():
    user_id = get_jwt_identity()
    activities = (
        StravaActivity.query.filter_by(user_id=user_id)
        .order_by(StravaActivity.start_date.desc())
        .limit(10)
        .all()
    )
    return jsonify([a.to_dict() for a in activities]), 200


@strava_bp.route("/login", methods=["GET"])
@jwt_required()
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


# 2. Rota de Callback (O Strava redireciona o usuário para cá após ele aceitar)
@strava_bp.route(
    "/callback", methods=["GET"]
)  # Certifique-se que não tem barra sobrando aqui se o Strava não envia
def strava_callback():
    code = request.args.get("code")
    user_id = request.args.get("state")  # Recuperamos o ID do paciente!
    error = request.args.get("error")

    # URL do seu frontend (Dashboard)
    FRONTEND_URL = "http://localhost:5173/dashboard"

    if error or not code or not user_id:
        print(f"[STRAVA] Erro na autorização ou dados ausentes: {error}")
        return redirect(f"{FRONTEND_URL}?strava_error=true")

    # 3. Trocamos o código temporário pelo Token de Acesso permanente
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

        # 4. Salva ou atualiza as chaves no cofre (PostgreSQL)
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


# 3. Rota auxiliar para o Frontend saber se o botão deve estar "Conectar" ou "Conectado"
@strava_bp.route("/status", methods=["GET"])
@jwt_required()
def strava_status():
    user_id = get_jwt_identity()
    cred = StravaCredentials.query.filter_by(user_id=user_id).first()

    if cred and cred.access_token:
        return jsonify({"connected": True}), 200

    return jsonify({"connected": False}), 200
