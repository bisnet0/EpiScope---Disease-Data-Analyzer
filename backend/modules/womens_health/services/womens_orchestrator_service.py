from backend.modules.womens_health.models.womens_models import WomensHealthAnalysis
from typing import Dict, Any, Optional

def get_integrated_health_report(patient_id: Optional[int] = None, consultation_type: str = "GENERAL") -> Dict[str, Any]:
    """
    Consolida as análises de Áudio e Vídeo para gerar um laudo multimodal.
    """
    # 1. Busca os últimos resultados no banco
    # Se patient_id for None, podemos buscar o último registro geral (para testes)
    query = WomensHealthAnalysis.query.filter_by(consultation_type=consultation_type)
    
    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    video_data = query.filter_by(exam_type='VIDEO').order_by(WomensHealthAnalysis.created_at.desc()).first()
    audio_data = query.filter_by(exam_type='AUDIO').order_by(WomensHealthAnalysis.created_at.desc()).first()

    # 2. Estrutura o retorno
    report = {
        "status": "pending",
        "multimodal_analysis": "Aguardando conclusão dos exames...",
        "alerts": [],
        "data": {
            "video": video_data.to_dict() if video_data else None,
            "audio": audio_data.to_dict() if audio_data else None
        }
    }

    # 3. Lógica de Cruzamento (O Pensamento do Maestro)
    if video_data and audio_data:
        report["status"] = "complete"
        
        # Exemplo de lógica de abrangência:
        v_dominant = video_data.dominant_result
        a_transcription = (audio_data.transcription or "").lower()

        if "estou bem" in a_transcription and "ALERTA" in v_dominant:
            report["multimodal_analysis"] = "🚨 INCONGRUÊNCIA CRÍTICA: Paciente nega queixas, mas biomarcadores indicam sofrimento."
            report["alerts"].append("RISCO_DISSOCIACAO")
        else:
            report["multimodal_analysis"] = "Sinais biomarcadores coerentes com o relato verbal."

    return report