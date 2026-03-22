import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from sqlalchemy import create_engine, text


class HospitalState(TypedDict):
    diagnosis: str
    severity: str
    ai_protocol: str
    blockchain_ref: str
    needs_emergency: bool


DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)


def clinical_analysis_node(state: HospitalState):
    diag = state["diagnosis"]
    print(f"🧠 [AI AUDITOR]: Analisando protocolo para {diag}...")

    # Lógica de severidade expandida
    keywords_grave = ["pneumonia", "glaucoma", "grave", "urgente", "high", "emergência"]
    severity = "HIGH" if any(w in diag.lower() for w in keywords_grave) else "LOW"

    # Protocolos específicos
    if "glaucoma" in diag.lower():
        protocol = f"Protocolo EpiScope (Oftalmo): Análise de escavação do disco óptico. Encaminhar para tonometria e mapeamento de retina."
    elif "raio-x" in diag.lower() or "pneumonia" in diag.lower():
        protocol = f"Protocolo EpiScope (Pulmonar): Análise de infiltrado alveolar. Sugerido isolamento e início de antibioticoterapia se confirmado."
    else:
        protocol = f"Protocolo EpiScope Geral: Monitoramento de {diag}. Conduta padrão sugerida."

    return {
        "ai_protocol": protocol,
        "severity": severity,
        "blockchain_ref": "PENDING_SIGNATURE",
    }


def save_to_db_node(state: HospitalState):
    """
    Salva a decisão clínica no banco.
    O status da blockchain fica como 'PENDING_SIGNATURE'.
    """
    print("💾 [DATABASE]: Persistindo decisão clínica no histórico...")

    query = text("""
        INSERT INTO clinical_decisions 
        (diagnosis, severity, protocol, blockchain_ref, needs_emergency)
        VALUES (:d, :s, :p, :b, :e)
    """)

    try:
        with engine.connect() as conn:
            conn.execute(
                query,
                {
                    "d": state["diagnosis"],
                    "s": state["severity"],
                    "p": state["ai_protocol"],
                    "b": state["blockchain_ref"],
                    "e": state.get("needs_emergency", False),
                },
            )
            conn.commit()
        print("✅ [DATABASE]: Registro salvo. Aguardando assinatura no Ledger.")
    except Exception as e:
        print(f"❌ [DATABASE] Erro ao salvar: {e}")

    return state


def emergency_node(state: HospitalState):
    print("🚨 [ALERT]: Notificando equipe médica!")
    return {"needs_emergency": True}


workflow = StateGraph(HospitalState)

workflow.add_node("analyze", clinical_analysis_node)
workflow.add_node("save", save_to_db_node)
workflow.add_node("emergency", emergency_node)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "save")

workflow.add_conditional_edges(
    "save", lambda x: x["severity"], {"HIGH": "emergency", "LOW": END}
)
workflow.add_edge("emergency", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n🚀 EXECUÇÃO MAESTRO EPISCOPE (MODO ASSÍNCRONO)\n")

    res = app.invoke({"diagnosis": "Dengue detectada"})
    print(f"\n✅ Finalizado: {res}")
