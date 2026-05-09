# backend/modules/womens_health/services/menstrual_service.py

from datetime import datetime, timedelta
from backend.modules.womens_health.models.womens_health_profile import (
    db,
    WomensHealthProfile,
)

# Importando os serviços das integrações
from backend.modules.integrations.models.google_fit_model import GoogleFitCredentials
from backend.modules.integrations.models.strava_model import StravaActivity
from backend.modules.integrations.services.google_fit_service import (
    get_google_fit_data_expanded,
)
from backend.modules.integrations.services.strava_service import sync_user_activities


def get_or_create_profile(user_id: str):
    profile = WomensHealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = WomensHealthProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile


def update_cycle_data_service(user_id: str, data: dict):
    profile = get_or_create_profile(user_id)

    try:
        if "last_period_start" in data:
            profile.last_period_start = datetime.strptime(
                data["last_period_start"], "%Y-%m-%d"
            ).date()
        if "average_cycle_length" in data:
            profile.average_cycle_length = int(data["average_cycle_length"])
        if "is_perimenopause" in data:
            profile.is_perimenopause = bool(data["is_perimenopause"])

        db.session.commit()
        return {
            "message": "Perfil ginecológico atualizado",
            "profile": profile.to_dict(),
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def _get_average_heart_rate(user_id: str):
    """
    Função Helper: Tenta buscar os batimentos do Google Fit.
    Se não achar ou não tiver token, faz fallback para a média de treinos do Strava.
    """
    recent_hr = 0
    hr_source = None

    # Tentativa 1: Google Fit (Mais preciso para Resting HR)
    fit_cred = GoogleFitCredentials.query.filter_by(user_id=user_id).first()
    if fit_cred and fit_cred.access_token:
        try:
            fit_data = get_google_fit_data_expanded(fit_cred.access_token)
            if fit_data and fit_data.get("bpm_avg", 0) > 0:
                recent_hr = round(fit_data["bpm_avg"])
                hr_source = "Google Fit"
        except Exception as e:
            print(f"⚠️ Erro ao ler Google Fit para ciclo menstrual: {e}")

    # Tentativa 2: Fallback para Strava (Média dos últimos treinos com HR)
    if recent_hr == 0:
        try:
            # Sincroniza e busca as atividades mais recentes
            sync_user_activities(user_id)
            recent_activities = (
                StravaActivity.query.filter_by(user_id=user_id, has_heartrate=True)
                .order_by(StravaActivity.start_date.desc())
                .limit(5)
                .all()
            )
            if recent_activities:
                total_hr = sum(
                    act.average_heartrate
                    for act in recent_activities
                    if act.average_heartrate
                )
                count = len([act for act in recent_activities if act.average_heartrate])
                if count > 0:
                    # Como o Strava é HR de treino (alto), calculamos uma estimativa aproximada de repouso
                    # (Apenas para fins de fallback preditivo, assumindo que repouso é ~60% do esforço leve)
                    avg_training_hr = total_hr / count
                    recent_hr = round(avg_training_hr * 0.6)
                    hr_source = "Strava (Estimativa)"
        except Exception as e:
            print(f"⚠️ Erro ao ler Strava para ciclo menstrual: {e}")

    return recent_hr, hr_source


def analyze_cycle_with_wearables(user_id: str):
    """
    Costura os dados da mulher com os dados de batimentos cardíacos
    do Google Fit e Strava para prever a fase do ciclo.
    """
    profile = get_or_create_profile(user_id)

    if not profile.last_period_start:
        return {
            "status": "pending",
            "message": "Necessário configurar a data da última menstruação para prever o ciclo.",
        }, 200

    # 1. Cálculos Baseados no Calendário
    today = datetime.utcnow().date()
    days_since_period = (today - profile.last_period_start).days
    cycle_length = profile.average_cycle_length

    # Identifica a fase (Incluindo o atraso!)
    current_phase = "Folicular"
    if days_since_period > cycle_length + 5:
        current_phase = (
            "Atraso Menstrual"  # 👈 Atualizamos a fase aqui em vez de dar return!
        )
    elif days_since_period < 5:
        current_phase = "Menstruação"
    elif cycle_length - 16 <= days_since_period <= cycle_length - 12:
        current_phase = "Ovulatória (Janela Fértil)"
    elif days_since_period > cycle_length - 12:
        current_phase = "Lútea"

    # 2. Busca Telemetria Cardíaca
    recent_hr, hr_source = _get_average_heart_rate(user_id)

    # 3. Geração de Insights Bio-Preditivos
    insights = []

    if recent_hr > 0:
        base_msg = f"Telemetria via {hr_source}: FC atual estimada em {recent_hr} BPM."
        insights.append(base_msg)

        if current_phase == "Lútea":
            insights.append(
                "Nota: Durante a fase lútea, o aumento da progesterona pode elevar a frequência cardíaca de repouso em 2 a 5 BPM."
            )
        elif current_phase == "Ovulatória (Janela Fértil)":
            insights.append(
                "Picos ligeiros na Frequência Cardíaca de Repouso (RHR) são comuns agora e ajudam a confirmar a ovulação."
            )
    else:
        insights.append(
            "Conecte seu Google Fit ou Strava para obter previsões cruzadas com sua Frequência Cardíaca."
        )

    if profile.is_perimenopause:
        insights.append(
            "Perimenopausa ativa: Oscilações hormonais podem causar flutuações atípicas no ciclo e na frequência cardíaca (palpitações)."
        )

    maestro_recommendation = None

    # Gatilho 1: Atraso Severo
    if days_since_period > cycle_length + 5:
        maestro_recommendation = f"⚠️ ALERTA CLÍNICO: Atraso menstrual de {days_since_period - cycle_length} dias. Avaliar possível gestação (beta-hCG) ou disfunção endócrina (SOP, tireoide)."

    # Gatilho 2: RHR muito alto fora da fase Lútea (Pode indicar infecção, estresse extremo ou hipertensão)
    elif recent_hr > 85 and current_phase != "Lútea":
        maestro_recommendation = f"🚨 ALERTA CARDIOVASCULAR: Frequência de repouso elevada ({recent_hr} BPM) fora do pico de progesterona. Avaliar resposta inflamatória, estresse metabólico ou risco cardiovascular."

    # Gatilho 3: Perimenopausa com RHR alto
    elif profile.is_perimenopause and recent_hr > 80:
        maestro_recommendation = "⚠️ ALERTA ENDÓCRINO: Paciente em perimenopausa apresentando taquicardia de repouso. Sugerida avaliação de reposição hormonal (TRH) e risco coronariano."

    else:
        maestro_recommendation = "ℹ️ Biometria e ciclo estabilizados. Padrões dentro da normalidade fisiológica."

    # Monta o Resultado Final
    next_period_estimate = profile.last_period_start + timedelta(days=cycle_length)

    analysis_result = {
        "status": "success",
        "current_day_of_cycle": days_since_period,  # Já corrigi para mostrar o dia exato
        "estimated_phase": current_phase,
        "next_period_prediction": next_period_estimate.isoformat(),
        "wearable_telemetry": {
            "heart_rate": recent_hr if recent_hr > 0 else None,
            "source": hr_source,
        },
        "clinical_insights": insights,
        "maestro_recommendation": maestro_recommendation,
    }

    return analysis_result, 200
