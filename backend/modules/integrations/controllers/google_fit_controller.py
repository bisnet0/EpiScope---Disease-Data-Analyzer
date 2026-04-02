import os
import time
import requests
from datetime import datetime, timedelta
from flask import request, jsonify, redirect
from flask_jwt_extended import get_jwt_identity


from backend.modules.auth.models.user_model import db
from backend.modules.integrations.services.google_fit_service import (
    get_google_fit_data,
    refresh_google_token,
)
from backend.modules.integrations.models.google_fit_model import (
    GoogleFitData,
    GoogleFitCredentials,
)

CLIENT_ID = os.environ.get("GOOGLE_FIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_FIT_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("GOOGLE_FIT_REDIRECT_URI", "")


def google_fit_login():
    user_id = str(get_jwt_identity())

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


def google_fit_callback():
    code = request.args.get("code")
    user_id = request.args.get("state")

    if not code or not user_id:
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

        expires_at = int(time.time()) + int(token_data.get("expires_in", 3600))
        access_token = str(token_data.get("access_token", ""))
        refresh_token = token_data.get("refresh_token")

        creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()

        if creds:
            creds.access_token = access_token
            creds.expires_at = expires_at
            if refresh_token:
                creds.refresh_token = str(refresh_token)
        else:
            creds = GoogleFitCredentials(
                user_id=str(user_id),
                access_token=access_token,
                expires_at=expires_at,
                refresh_token=str(refresh_token) if refresh_token else None,
            )
            db.session.add(creds)

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


def google_fit_status():
    user_id = str(get_jwt_identity())
    creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()
    return jsonify({"connected": creds is not None}), 200


def sync_google_data():
    user_id = str(get_jwt_identity())
    creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()

    if not creds:
        return jsonify({"error": "Não conectado"}), 404

    if int(time.time()) >= (int(creds.expires_at) - 60):
        print("🔄 Token expirado! Renovando...")
        new_tokens = refresh_google_token(str(creds.refresh_token))
        if new_tokens:
            creds.access_token = new_tokens["access_token"]
            creds.expires_at = int(time.time()) + int(new_tokens["expires_in"])
            db.session.commit()
            print("✅ Token renovado com sucesso!")
        else:
            return jsonify(
                {"error": "Falha ao renovar acesso. Faça login novamente."}
            ), 401

    try:
        metrics = get_google_fit_data(str(creds.access_token))

        if metrics:
            now = datetime.now()

            dates_to_update = [now.date(), (now - timedelta(days=1)).date()]

            for target_date in dates_to_update:
                entry = GoogleFitData.query.filter_by(
                    user_id=user_id, date=target_date
                ).first()

                if entry:
                    entry.steps = int(metrics.get("steps", 0))
                    entry.sleep_minutes = int(metrics.get("sleep_minutes", 0))
                    entry.resting_hr = metrics.get("resting_hr")
                    entry.last_sync = datetime.utcnow()
                else:
                    entry = GoogleFitData(
                        user_id=user_id,
                        date=target_date,
                        steps=int(metrics.get("steps", 0)),
                        sleep_minutes=int(metrics.get("sleep_minutes", 0)),
                        resting_hr=metrics.get("resting_hr"),
                        last_sync=datetime.utcnow(),
                    )
                    db.session.add(entry)

            db.session.commit()
            return jsonify({"message": "Sincronizado", "data": metrics}), 200
    except Exception as e:
        print(f"❌ Erro no sync: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Falha ao obter dados"}), 500


def get_metrics():
    user_id = str(get_jwt_identity())
    today = datetime.now().date()

    data = GoogleFitData.query.filter_by(user_id=user_id, date=today).first()

    if data:
        return jsonify(
            {
                "steps": int(data.steps) if data.steps else 0,
                "sleep_minutes": int(data.sleep_minutes) if data.sleep_minutes else 0,
                "resting_hr": float(data.resting_hr) if data.resting_hr else 0,
                "bpm_min": float(data.resting_hr) if data.resting_hr else 0,
            }
        ), 200

    return jsonify({"steps": 0, "sleep_minutes": 0, "resting_hr": 0, "bpm_min": 0}), 200


def disconnect_google_fit():
    user_id = str(get_jwt_identity())
    try:
        creds = GoogleFitCredentials.query.filter_by(user_id=user_id).first()

        if creds:
            db.session.delete(creds)
            db.session.commit()
            print(
                f"✅ Google Fit desconectado para o usuário {user_id}. Dados preservados."
            )
            return jsonify(
                {
                    "message": "Conexão com Google Fit removida. Seus dados históricos foram mantidos."
                }
            ), 200

        return jsonify({"message": "Nenhuma conexão ativa encontrada."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao desconectar: {str(e)}"}), 500
        db.session.rollback()
        return jsonify({"error": f"Erro ao desconectar: {str(e)}"}), 500
