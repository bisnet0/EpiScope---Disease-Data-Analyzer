from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text

# 👇 Imports mantidos (serão atualizados conforme as pastas mudarem)
from backend.modules.blockchain.services.blockchain_service import process_ledger_registration
from backend.modules.core_agent.agents.hospital_workflow import engine
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
        with engine.connect() as conn:
            conn.execute(query_audit, {"tx": tx_hash})

            conn.execute(query_ledger, {"d_id": diag_id, "h": tx_hash, "tx": tx_hash})
            conn.commit()

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