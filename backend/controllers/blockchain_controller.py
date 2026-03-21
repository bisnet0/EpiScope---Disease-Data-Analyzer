from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user_model import db
from backend.models.diagnosis_model import (
    ArbovirusDiagnosis,
    GlaucomaDiagnosis,
    XRayDiagnosis,
)


def register_blockchain_ledger():
    user_id = get_jwt_identity()
    data = request.json

    diag_id = data.get("diagnosis_id")
    diag_type = data.get("type")
    tx_hash = data.get("tx_hash")

    if not all([diag_id, diag_type, tx_hash]):
        return jsonify({"error": "Dados incompletos"}), 400

    model_map = {
        "ARBOVIROSE": ArbovirusDiagnosis,
        "GLAUCOMA": GlaucomaDiagnosis,
        "RAIO-X (TÓRAX)": XRayDiagnosis,
    }

    model = model_map.get(diag_type.upper())
    if not model:
        return jsonify({"error": "Tipo de diagnóstico inválido"}), 400

    item = model.query.filter_by(id=diag_id, user_id=user_id).first()

    if not item:
        return jsonify({"error": "Diagnóstico não encontrado"}), 404

    item.blockchain_hash = tx_hash
    db.session.commit()

    return jsonify(
        {
            "status": "success",
            "message": f"Assinatura {diag_type} registrada!",
            "tx_hash": tx_hash,
        }
    ), 201
