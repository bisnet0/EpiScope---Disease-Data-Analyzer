from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from langchain.tools import tool

# 👇 O import do modelo (temporário até refatorar a pasta models)
from backend.models.health_model import StravaActivity


def get_safe_user_id():
    """Busca o usuário do Token (se API) ou o primeiro do banco (se Terminal)"""
    if has_request_context():
        try:
            return get_jwt_identity()
        except:
            pass

    from backend.models.user_model import User
    admin = User.query.first()
    return admin.id if admin else None


@tool("health_metrics_tool")
def health_metrics_tool(query: str = None):
    """
    Busca o histórico de saúde, atividades físicas e frequência cardíaca do usuário no Strava.
    Use esta ferramenta quando o usuário reclamar de cansaço, dor no corpo, palpitações,
    ou quando quiser saber se a rotina física dele influencia no diagnóstico atual.
    """
    user_id = get_safe_user_id()
    if not user_id:
        return "Usuário não identificado."

    # Pegamos as últimas 5 atividades para análise de tendência
    activities = (
        StravaActivity.query.filter_by(user_id=user_id)
        .order_by(StravaActivity.start_date.desc())
        .limit(5)
        .all()
    )

    if not activities:
        return "O usuário ainda não tem dados de atividades físicas sincronizados."

    report = "[RELATÓRIO FISIOLÓGICO DO PACIENTE]\n"
    for a in activities:
        hr_status = (
            f"{a.average_heartrate} BPM (Méd)"
            if a.has_heartrate
            else "Sem sensor de RH"
        )
        report += f"- {a.start_date.date()}: {a.name} ({a.activity_type}) | Esforço: {hr_status} | Duração: {a.moving_time_seconds // 60}min\n"

    return report