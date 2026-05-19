import json
from sqlalchemy import text
from backend.modules.core_agent.agents.hospital_workflow import engine


def process_ledger_registration(user_id, diagnosis_id, tx_hash, payload):
    """
    Persiste o registro de auditoria na tabela blockchain_ledger usando SQL Puro.
    """
    query = text("""
        INSERT INTO blockchain_ledger 
        (diagnosis_id, payload_hash, transaction_hash, status, timestamp)
        VALUES (:diag_id, :p_hash, :tx_hash, 'confirmed', NOW())
    """)

    try:
        with engine.connect() as conn:
            conn.execute(
                query,
                {
                    "diag_id": diagnosis_id,
                    "p_hash": tx_hash,
                    "tx_hash": tx_hash,
                },
            )
            conn.commit()
        print(
            f"✅ [LEDGER]: Registro inserido em blockchain_ledger para ID {diagnosis_id}"
        )
        return True
    except Exception as e:
        print(f"❌ [LEDGER ERROR]: {e}")
        return False
