from langchain.tools import tool
from typing import Dict, Any
from backend.modules.womens_health.services.womens_orchestrator_service import (
    get_integrated_health_report,
)
from backend.modules.womens_health.services.menstrual_service import (
    analyze_cycle_with_wearables,
)
from flask_jwt_extended import get_jwt_identity


@tool
def analyze_vocal_distress_tool(
    acoustic_metrics: Dict[str, Any], consultation_type: str
) -> str:
    """
    Analisa métricas acústicas (hesitação, volume e variância de tom) para detectar
    sinais de distress emocional, medo ou patologias em contextos de saúde da mulher.
    Use esta ferramenta quando receber dados de 'acoustic_metrics'.
    """

    hesitation = acoustic_metrics.get("hesitation_ratio", 0)
    volume = acoustic_metrics.get("mean_volume", 0)
    pitch_var = acoustic_metrics.get("pitch_variance", 0)

    report = []

    if consultation_type == "TRIAGEM_VIOLENCIA":
        if volume < 0.01 and hesitation > 0.3:
            report.append(
                "IDENTIFICADO: Padrão de fala 'sussurrado' com bloqueios silábicos (hesitação alta)."
            )
            report.append(
                "INTERPRETAÇÃO: Compatível com estado de hipervigilância ou medo agudo."
            )
        else:
            report.append("Padrão vocal estável para o contexto de triagem.")

    elif consultation_type == "POS_PARTO":
        if hesitation > 0.4 and pitch_var < 100:
            report.append(
                "IDENTIFICADO: Fala monótona (flat affect) e lentidão no processamento verbal."
            )
            report.append(
                "INTERPRETAÇÃO: Indicativo clínico de possível depressão pós-parto (DPP)."
            )

    if not report:
        return "As métricas acústicas estão dentro dos parâmetros basais para este tipo de consulta."

    return " | ".join(report)


@tool
def analyze_facial_incongruence_tool(video_metrics: Dict[str, Any]) -> str:
    """
    Interpreta as emoções dominantes e detecta se a expressão facial
    condiz com o relato clínico da paciente.
    Use quando 'video_analysis' estiver disponível.
    """
    emotion = video_metrics.get("dominant_emotion", "neutral")
    dist = video_metrics.get("emotion_distribution", {})
    alerts = video_metrics.get("clinical_alerts", [])

    report = f"Emoção predominante detectada: {emotion.upper()}."

    if "happy" in dist and dist["happy"] > 0.15:
        report += " | ALERTA: Presença de 'Riso Inadequado' ou Afeto Incongruente."

    if alerts:
        report += f" | Sugestão: {alerts[0]}"

    return report


@tool
def analyze_multimodal_womens_health(
    audio_metrics: Dict[str, Any], video_metrics: Dict[str, Any], transcription: str
) -> str:
    """
    Analisa a correlação entre voz, rosto e discurso.
    Cruza emoções (Raiva, Medo, Tristeza, Nojo, etc.) com métricas acústicas.
    """

    emotion = video_metrics.get("dominant_emotion", "neutral")
    dist = video_metrics.get("emotion_distribution", {})

    hesitation = audio_metrics.get("hesitation_ratio", 0)

    analysis_parts = [
        f"CONTEXTO MULTIMODAL: A transcrição indica: '{transcription[:100]}...'"
    ]

    if emotion == "sad":
        analysis_parts.append(
            "Veredito Facial: Tristeza profunda detectada. Requer acolhimento."
        )
    elif emotion == "fear":
        analysis_parts.append(
            "Veredito Facial: Sinais de MEDO ou PAVOR. Prioridade Máxima em segurança."
        )
    elif emotion == "angry":
        analysis_parts.append(
            "Veredito Facial: Expressão de RAIVA ou IRRITABILIDADE. Pode indicar reatividade ao trauma."
        )
    elif emotion == "disgust":
        analysis_parts.append(
            "Veredito Facial: Expressão de NOJO/AVERSÃO. Comum em relatos de abuso ou desconforto físico."
        )
    elif emotion == "surprise":
        analysis_parts.append(
            "Veredito Facial: SURPRESA detectada. Verificar se condiz com o relato de fatos inesperados."
        )
    else:
        analysis_parts.append(
            "Veredito Facial: Expressão Neutra ou sob controle emocional."
        )

    if (emotion in ["sad", "fear"]) and (dist.get("happy", 0) > 0.15):
        analysis_parts.append(
            "⚠️ ALERTA DE INCONGRUÊNCIA: Riso inadequado detectado em contexto de sofrimento (Mecanismo de Defesa)."
        )

    if hesitation > 0.4 and emotion == "sad":
        analysis_parts.append(
            "⚠️ ALERTA: Alta latência na fala combinada com tristeza facial. Possível depressão oculta."
        )

    return " | ".join(analysis_parts)


@tool
def fetch_womens_health_biomarkers(consultation_type: str = "GENERAL") -> str:
    """
    Busca os biomarcadores de áudio e vídeo mais recentes para um tipo de consulta.
    Útil para identificar incongruências emocionais e estados de saúde mental.
    """
    try:
        report = get_integrated_health_report(consultation_type=consultation_type)

        if report["status"] == "pending":
            return "Ainda não há dados suficientes de áudio ou vídeo processados para esta consulta."

        video_dominant = report["data"]["video"]["dominant_result"]
        audio_transcription = (
            report["data"]["audio"]["transcription"] or "Não transcrito"
        )

        return (
            f"RESULTADO MULTIMODAL:\n"
            f"- Análise de Vídeo: {video_dominant}\n"
            f"- Transcrição do Áudio: {audio_transcription}\n"
            f"- Alerta do Sistema: {report['multimodal_analysis']}"
        )
    except Exception as e:
        return f"Erro ao acessar biomarcadores: {str(e)}"


@tool
def fetch_menstrual_cycle_biomarkers() -> str:
    """
    Busca os dados preditivos do ciclo menstrual da paciente, cruzados com
    telemetria de wearables (Google Fit / Strava), incluindo a Frequência Cardíaca de Repouso (RHR)
    e alertas de atraso ou perimenopausa.
    """
    try:
        current_user_id = get_jwt_identity()

        if not current_user_id:
            return (
                "Erro: Token de acesso necessário para buscar dados sensíveis de ciclo."
            )

        # Desempacotando e tipando explicitamente para o Pylance
        response_tuple = analyze_cycle_with_wearables(current_user_id)
        result: dict = response_tuple[0]
        status: int = response_tuple[1]

        if status != 200 or result.get("status") == "pending":
            return "Os dados de ciclo menstrual ainda não foram calibrados ou estão indisponíveis."

        # 👇 A MÁGICA PRA CALAR O PYLANCE: Verificação estrita de tipo
        telemetry = result.get("wearable_telemetry")
        if not isinstance(telemetry, dict):
            telemetry = {}

        hr = telemetry.get("heart_rate") or "N/A"
        source = telemetry.get("source") or "N/A"

        report = (
            f"🩺 RELATÓRIO PREDITIVO DE CICLO E WEARABLES:\n"
            f"- Dia do Ciclo Atual: {result.get('current_day_of_cycle')}\n"
            f"- Fase Estimada: {result.get('estimated_phase')}\n"
            f"- Frequência Cardíaca de Repouso (RHR): {hr} BPM (Fonte: {source})\n"
            f"- Previsão da Próxima Menstruação: {result.get('next_period_prediction')}\n\n"
            f"💡 INSIGHTS CLÍNICOS:\n"
        )

        # Garantindo que é uma lista pro Pylance não chiar
        insights = result.get("clinical_insights")
        if isinstance(insights, list):
            for insight in insights:
                report += f"  * {insight}\n"

        maestro_alert = result.get("maestro_recommendation")
        if isinstance(maestro_alert, str) and maestro_alert:
            report += f"\n🚨 ALERTA ATIVO DO SISTEMA:\n  * {maestro_alert}"

        return report

    except Exception as e:
        return f"Erro ao acessar biomarcadores de ciclo: {str(e)}"
