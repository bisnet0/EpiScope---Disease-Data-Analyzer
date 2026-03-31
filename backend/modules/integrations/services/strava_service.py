import requests
import os
from datetime import datetime
from backend.modules.auth.models.user_model import db
from backend.modules.integrations.models.strava_model import StravaCredentials, StravaActivity


def refresh_strava_token(cred):
    """Atualiza o token de acesso se estiver expirado"""
    print(f"[STRAVA] Atualizando token para o usuário {cred.user_id}...")

    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": os.environ.get("STRAVA_CLIENT_ID"),
        "client_secret": os.environ.get("STRAVA_CLIENT_SECRET"),
        "refresh_token": cred.refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        data = response.json()
        cred.access_token = data["access_token"]
        cred.refresh_token = data["refresh_token"]
        cred.expires_at = data["expires_at"]
        db.session.commit()
        return data["access_token"]
    return None


def sync_user_activities(user_id):
    """Puxa as últimas 30 atividades do Strava e salva no banco"""
    cred = StravaCredentials.query.filter_by(user_id=user_id).first()
    if not cred:
        return False

    # Verifica expiração (com margem de 5 min)
    token = cred.access_token
    if datetime.utcnow().timestamp() > (cred.expires_at - 300):
        token = refresh_strava_token(cred)

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"per_page": 30}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return False

    activities = response.json()
    for act in activities:
        exists = StravaActivity.query.filter_by(
            strava_activity_id=str(act["id"])
        ).first()

        # Se não existe, vamos extrair TUDO
        if not exists:
            new_act = StravaActivity(
                user_id=user_id,
                strava_activity_id=str(act["id"]),
                name=act.get("name"),
                activity_type=act.get("type"),
                distance_meters=act.get("distance", 0),
                moving_time_seconds=act.get("moving_time", 0),
                # Dados Cardíacos (Garante que pega se existir)
                has_heartrate=act.get("has_heartrate", False),
                average_heartrate=act.get("average_heartrate"),
                max_heartrate=act.get("max_heartrate"),
                # Dados de Potência e Ambiente
                average_watts=act.get("average_watts"),
                max_watts=act.get("max_watts"),
                average_temp=act.get("average_temp"),
                elev_high=act.get("elev_high"),
                start_date=datetime.strptime(
                    act["start_date_local"], "%Y-%m-%dT%H:%M:%SZ"
                ),
                raw_data=act,  # Mantemos o JSON bruto para o Agente IA "escarafunchar"
            )
            db.session.add(new_act)

    db.session.commit()
    return True
