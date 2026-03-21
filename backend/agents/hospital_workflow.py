import os
import torch
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from sqlalchemy import create_engine, text
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


class HospitalState(TypedDict):
    diagnosis: str
    severity: str
    ai_protocol: str
    blockchain_ref: str
    needs_emergency: bool


MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
ADAPTER_PATH = "/app/medical_assistant_adapter"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, torch_dtype=torch.float16, device_map="auto"
)
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)


def clinical_analysis_node(state: HospitalState):
    """Consulta o Assistant Tunado para definir o protocolo"""
    diag = state["diagnosis"]
    prompt = f"### Instruction:\nQual o protocolo e gravidade para o diagnóstico de {diag}?\n\n### Response:\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100)
        response = (
            tokenizer.decode(outputs[0], skip_special_tokens=True)
            .split("### Response:")[-1]
            .strip()
        )

    keywords_grave = ["grave", "urgente", "high", "emergência", "pneumonia", "98", "99"]
    severity = (
        "HIGH" if any(word in response.lower() for word in keywords_grave) else "LOW"
    )

    print(f"🧠 [AI AUDITOR]: {response}")
    return {"ai_protocol": response, "severity": severity}


def blockchain_node(state: HospitalState):
    """Simula o registro imutável do diagnóstico"""
    print(
        f"🔗 [BLOCKCHAIN]: Registrando laudo de '{state['diagnosis']}' para fins de auditoria..."
    )
    return {"blockchain_ref": "0xABC123...EPISCOPE"}


def emergency_node(state: HospitalState):
    """Nodo acionado apenas em casos graves"""
    print(f"🚨 [ALERT]: Notificando equipe médica! Caso de alta severidade detectado.")
    return {"needs_emergency": True}


def save_to_db_node(state: HospitalState):
    print("💾 [DATABASE]: Salvando decisão clínica no histórico SQL...")

    insert_query = text("""
        INSERT INTO clinical_decisions 
        (diagnosis, severity, protocol, blockchain_ref, needs_emergency)
        VALUES (:diagnosis, :severity, :protocol, :blockchain_ref, :needs_emergency)
    """)

    try:
        with engine.connect() as conn:
            conn.execute(
                insert_query,
                {
                    "diagnosis": state["diagnosis"],
                    "severity": state["severity"],
                    "protocol": state["ai_protocol"],
                    "blockchain_ref": state.get("blockchain_ref", "N/A"),
                    "needs_emergency": state.get("needs_emergency", False),
                },
            )
            conn.commit()
        print("✅ [DATABASE]: Registro salvo com sucesso.")
    except Exception as e:
        print(f"❌ [DATABASE] Erro ao salvar: {e}")

    return state


workflow = StateGraph(HospitalState)


workflow.add_node("analyze", clinical_analysis_node)
workflow.add_node("audit", blockchain_node)
workflow.add_node("save_db", save_to_db_node)
workflow.add_node("emergency", emergency_node)


workflow.set_entry_point("analyze")

workflow.add_edge("analyze", "audit")
workflow.add_edge("audit", "save_db")


workflow.add_conditional_edges(
    "save_db", lambda x: x["severity"], {"HIGH": "emergency", "LOW": END}
)

workflow.add_edge("emergency", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n🚀 Iniciando Fluxo de Decisão EpiScope...\n")

    initial_state = {"diagnosis": "Pneumonia detectada no Raio-X"}
    final_output = app.invoke(initial_state)

    print("\n✅ Fluxo Finalizado.")
    print(f"Resultado Final: {final_output}")
