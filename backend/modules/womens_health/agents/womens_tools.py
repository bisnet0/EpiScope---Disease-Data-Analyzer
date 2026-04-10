from langchain.tools import tool
from typing import Dict, Any

@tool
def analyze_vocal_distress_tool(acoustic_metrics: Dict[str, Any], consultation_type: str) -> str:
    """
    Analisa métricas acústicas (hesitação, volume e variância de tom) para detectar 
    sinais de distress emocional, medo ou patologias em contextos de saúde da mulher.
    Use esta ferramenta quando receber dados de 'acoustic_metrics'.
    """
    
    hesitation = acoustic_metrics.get("hesitation_ratio", 0)
    volume = acoustic_metrics.get("mean_volume", 0)
    pitch_var = acoustic_metrics.get("pitch_variance", 0)
    
    report = []
    
    # Lógica de interpretação para o Agente
    if consultation_type == "TRIAGEM_VIOLENCIA":
        if volume < 0.01 and hesitation > 0.3:
            report.append("IDENTIFICADO: Padrão de fala 'sussurrado' com bloqueios silábicos (hesitação alta).")
            report.append("INTERPRETAÇÃO: Compatível com estado de hipervigilância ou medo agudo.")
        else:
            report.append("Padrão vocal estável para o contexto de triagem.")

    elif consultation_type == "POS_PARTO":
        if hesitation > 0.4 and pitch_var < 100:
            report.append("IDENTIFICADO: Fala monótona (flat affect) e lentidão no processamento verbal.")
            report.append("INTERPRETAÇÃO: Indicativo clínico de possível depressão pós-parto (DPP).")
            
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