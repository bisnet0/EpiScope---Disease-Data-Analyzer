from datetime import timezone
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

# 👇 Imports temporários apontando para a pasta raiz de models
from backend.models.diagnosis_model import (
    ArbovirusDiagnosis,
    GlaucomaDiagnosis,
    XRayDiagnosis,
)

def get_user_history():
    """
    Busca e consolida o histórico de todos os diagnósticos (Arbovírus, Glaucoma, Raio-X)
    do paciente logado, ordenando do mais recente para o mais antigo.
    """
    current_user_id = get_jwt_identity()

    arbovirus = ArbovirusDiagnosis.query.filter_by(user_id=current_user_id).all()
    glaucoma = GlaucomaDiagnosis.query.filter_by(user_id=current_user_id).all()
    xray = XRayDiagnosis.query.filter_by(user_id=current_user_id).all()
    
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

    # Ordena a timeline cronologicamente (do mais recente pro mais antigo)
    history.sort(key=lambda x: x["date"], reverse=True)
    
    return jsonify(history), 200