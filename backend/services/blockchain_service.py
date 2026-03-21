import json
from backend.models.user_model import db
from backend.models.blockchain_model import BlockchainLedger

def process_ledger_registration(user_id, diagnosis_id, tx_hash, payload):
    """
    Valida e persiste o registro de auditoria.
    """
    try:
        # Aqui, no futuro, você pode bater no endpoint do nonodo (localhost:8080)
        # para verificar se a transação realmente existe lá.
        
        # Por hora, registramos a intenção confirmada pelo Front
        new_entry = BlockchainLedger(
            diagnosis_id=diagnosis_id,
            user_id=user_id,
            tx_hash=tx_hash,
            payload_json=payload,
            status='confirmed'
        )
        
        db.session.add(new_entry)
        db.session.commit()
        return True
    except Exception as e:
        print(f"❌ Erro no Ledger Service: {e}")
        db.session.rollback()
        return False