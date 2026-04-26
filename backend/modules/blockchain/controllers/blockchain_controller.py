from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text

from backend.modules.blockchain.services.blockchain_service import (
    process_ledger_registration,
)
from backend.modules.core_agent.agents.hospital_workflow import engine
from backend.modules.auth.models.user_model import db

from backend.modules.arbovirus.models.arbovirus_model import ArbovirusDiagnosis
from backend.modules.glaucoma.models.glaucoma_model import GlaucomaDiagnosis
from backend.modules.chest_xray.models.xray_model import XRayDiagnosis

# 👇 1. Importe o novo Model
from backend.modules.womens_health.models.womens_models import WomensHealthAnalysis


def register_blockchain_ledger():
    user_id = str(get_jwt_identity())

    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "JSON inválido"}), 400

    diag_id = data.get("diagnosis_id")
    diag_type = data.get("type")
    tx_hash = data.get("tx_hash")

    if not diag_id or not isinstance(diag_type, str) or not tx_hash:
        return jsonify({"error": "Dados incompletos ou inválidos"}), 400

    model_map = {
        "ARBOVIROSE": ArbovirusDiagnosis,
        "GLAUCOMA": GlaucomaDiagnosis,
        "RAIO-X (TÓRAX)": XRayDiagnosis,
        "SAÚDE DA MULHER": WomensHealthAnalysis,
    }

    model = model_map.get(diag_type.upper())

    if model is None:
        return jsonify({"error": f"Tipo de diagnóstico desconhecido: {diag_type}"}), 400

    if diag_type.upper() == "SAÚDE DA MULHER":
        item = model.query.filter_by(id=diag_id, patient_id=user_id).first()
    else:
        item = model.query.filter_by(id=diag_id, user_id=user_id).first()

    if item:
        item.blockchain_hash = tx_hash
        db.session.commit()

    query_audit = text("""
        UPDATE clinical_decisions 
        SET blockchain_ref = :tx
        WHERE id = (
            SELECT id FROM clinical_decisions 
            WHERE blockchain_ref = 'PENDING_SIGNATURE' 
            ORDER BY id DESC LIMIT 1
        )
    """)

    query_ledger = text("""
        INSERT INTO blockchain_ledger 
        (diagnosis_id, payload_hash, transaction_hash, status, timestamp)
        VALUES (:d_id, :h, :tx, 'confirmed', NOW())
    """)

    try:
        with engine.begin() as conn:
            conn.execute(query_audit, {"tx": str(tx_hash)})

            conn.execute(
                query_ledger,
                {"d_id": str(diag_id), "h": str(tx_hash), "tx": str(tx_hash)},
            )

        print(f"🚀 [SUCESSO]: Tabelas clinical_decisions e ledger atualizadas via SQL!")
        return jsonify(
            {
                "status": "success",
                "message": "Assinatura registrada e auditoria finalizada!",
                "tx_hash": tx_hash,
            }
        ), 201

    except Exception as e:
        print(f"❌ [ERRO SQL]: {e}")
        return jsonify({"error": str(e)}), 500
