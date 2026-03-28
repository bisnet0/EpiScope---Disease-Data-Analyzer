import json
import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 📂 CONFIGURAÇÃO DE DIRETÓRIOS E CAMINHOS
# ==========================================
# SCRIPT_DIR = backend/modules/core_agent/ml-workflow
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# MODULE_DIR = backend/modules/core_agent
MODULE_DIR = os.path.dirname(SCRIPT_DIR)

# 🎯 Pasta exclusiva para os artefatos gerados pelo LLM
TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")
os.makedirs(TRAIN_RESULTS_DIR, exist_ok=True)

DATASET_SAVE_PATH = os.path.join(TRAIN_RESULTS_DIR, "training_data_lora.jsonl")

def generate_medical_instructions():
    print("🤖 Iniciando geração de dataset para Fine-Tuning do LLM (LoRA)...")
    
    DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    engine = create_engine(DB_URL)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT model_name, accuracy, metrics FROM model_training_logs")
            )

            instructions = []
            for row in result:
                # Tratamento de segurança caso a acurácia venha nula
                acc = row.accuracy if row.accuracy is not None else 0.0
                metrics_data = row.metrics if row.metrics else "{}"
                
                instructions.append(
                    {
                        "instruction": f"Qual a performance do modelo {row.model_name}?",
                        "context": "Resultados de Treinamento Interno - EpiScope",
                        "response": f"O modelo {row.model_name} apresenta acurácia de {acc:.2%}. {metrics_data}",
                    }
                )

            # Salvando na pasta correta com encoding seguro para PT-BR
            with open(DATASET_SAVE_PATH, "w", encoding="utf-8") as f:
                for entry in instructions:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"✅ Dataset para Fine-Tuning LoRA gerado com dados REAIS do banco!")
        print(f"📁 Salvo em: {DATASET_SAVE_PATH}")
        print(f"📊 Total de instruções geradas: {len(instructions)}")

    except Exception as e:
        print(f"❌ Erro ao gerar o dataset LoRA: {e}")

if __name__ == "__main__":
    generate_medical_instructions()