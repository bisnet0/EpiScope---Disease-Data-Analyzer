from datetime import timedelta
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv


from backend.modules.auth.models.user_model import db
from backend.modules.profile.models.profile_model import UserProfile
from backend.modules.arbovirus.models.arbovirus_model import ArbovirusDiagnosis
from backend.modules.glaucoma.models.glaucoma_model import GlaucomaDiagnosis
from backend.modules.laboratory.models.ml_log_model import ModelTrainingLog
from backend.modules.integrations.models.strava_model import (
    StravaCredentials,
    StravaActivity,
)
from backend.modules.integrations.models.google_fit_model import (
    GoogleFitData,
    GoogleFitCredentials,
)
from backend.modules.blockchain.models.blockchain_model import BlockchainLedger


from backend.modules.auth.routes.auth_routes import auth_bp
from backend.modules.core_agent.routes.agent_routes import agent_bp
from backend.modules.core_agent.routes.workflow_routes import workflow_bp
from backend.modules.glaucoma.routes.glaucoma_routes import glaucoma_bp
from backend.modules.arbovirus.routes.arbovirus_routes import arbovirus_bp
from backend.modules.integrations.routes.google_fit_routes import google_fit_bp
from backend.modules.integrations.routes.strava_routes import strava_bp
from backend.modules.laboratory.routes.lab_routes import lab_bp
from backend.modules.dashboard.routes.dashboard_routes import dashboard_bp
from backend.modules.chest_xray.routes.xray_routes import xray_bp
from backend.modules.blockchain.routes.blockchain_routes import blockchain_bp
from backend.modules.patients.routes.history_routes import history_bp
from backend.modules.womens_health.routes.womens_health_routes import womens_health_bp
from backend.modules.profile.routes.profile_routes import profile_bp


load_dotenv()

app = Flask(__name__)


CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)


db.init_app(app)
jwt = JWTManager(app)


app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(agent_bp, url_prefix="/api/agent")
app.register_blueprint(glaucoma_bp, url_prefix="/api/glaucoma")
app.register_blueprint(arbovirus_bp, url_prefix="/api/arbovirus")
app.register_blueprint(google_fit_bp, url_prefix="/api/integrations/google-fit")
app.register_blueprint(strava_bp, url_prefix="/api/integrations/strava")
app.register_blueprint(lab_bp, url_prefix="/api/laboratory")
app.register_blueprint(workflow_bp, url_prefix="/api/workflow")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(xray_bp, url_prefix="/api/chest-xray")
app.register_blueprint(blockchain_bp, url_prefix="/api/blockchain")
app.register_blueprint(history_bp, url_prefix="/api/patients")
app.register_blueprint(womens_health_bp, url_prefix="/api/womens-health")
app.register_blueprint(profile_bp, url_prefix="/api/profile")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
