import os
import requests
from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user_model import db

google_fit_bp = Blueprint("google_fit", __name__)

CLIENT_ID = os.environ.get("GOOGLE_FIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_FIT_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("GOOGLE_FIT_REDIRECT_URI")

@google_fit_bp.route("/login", methods=["GET"])
@jwt_required()
def google_fit_login():
    user_id = get_jwt_identity()
    
    # Escopos para Passos, Atividades e Batimentos
    scopes = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read"
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
        return redirect("http://localhost:5173/dashboard?google_error=true")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    res = requests.post(token_url, data=data)
    if res.status_code == 200:
        # Aqui você salvaria no banco (Similar ao StravaCredentials)
        # Ex: GoogleFitCredentials(user_id=user_id, access_token=...)
        print(f"✅ Google Fit conectado para o usuário {user_id}")
        return redirect("http://localhost:5173/dashboard?google_success=true")
    
    return redirect("http://localhost:5173/dashboard?google_error=token_fail")