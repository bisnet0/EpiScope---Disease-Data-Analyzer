from datetime import timezone
from flask import jsonify
from flask_jwt_extended import get_jwt_identity


from backend.modules.arbovirus.models.arbovirus_model import ArbovirusDiagnosis
from backend.modules.glaucoma.models.glaucoma_model import GlaucomaDiagnosis
from backend.modules.chest_xray.models.xray_model import XRayDiagnosis


from backend.modules.womens_health.models.womens_models import WomensHealthAnalysis


def get_user_history():
    """
    Busca e consolida o histórico de todos os diagnósticos (Arbovírus, Glaucoma, Raio-X e Saúde da Mulher)
    do paciente logado, ordenando do mais recente para o mais antigo.
    """
    current_user_id = get_jwt_identity()

    arbovirus = ArbovirusDiagnosis.query.filter_by(user_id=current_user_id).all()
    glaucoma = GlaucomaDiagnosis.query.filter_by(user_id=current_user_id).all()
    xray = XRayDiagnosis.query.filter_by(user_id=current_user_id).all()

    womens_health = WomensHealthAnalysis.query.filter_by(
        patient_id=current_user_id
    ).all()

    history = []

    for item in arbovirus:
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )
        history.append(
            {
                "id": item.id,
                "type": "Arbovirose",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": f"Sintomas: {item.text_description[:40]}..."
                if item.text_description
                else "Descrição não disponível",
                "result": item.prediction_result,
                "signature": tx_hash,
            }
        )

    for item in glaucoma:
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )
        history.append(
            {
                "id": item.id,
                "type": "Glaucoma",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": "Imagem de Fundo de Olho (Processada)",
                "result": item.prediction_result,
                "signature": tx_hash,
            }
        )

    for item in xray:
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )
        history.append(
            {
                "id": item.id,
                "type": "RAIO-X (TÓRAX)",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": "Radiografia Pulmonar (Processada via CNN)",
                "result": item.prediction_result,
                "signature": tx_hash,
            }
        )

    for item in womens_health:
        tx_hash = getattr(item, "blockchain_hash", None) or getattr(
            item, "tx_hash", None
        )
        history.append(
            {
                "id": str(item.id),
                "type": "Saúde da Mulher",
                "date": item.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "details": f"Análise Multimodal ({item.exam_type})",
                "result": item.dominant_result,
                "signature": tx_hash,
            }
        )

    history.sort(key=lambda x: x["date"], reverse=True)

    return jsonify(history), 200
