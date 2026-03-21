import json
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os


def generate_medical_instructions():
    DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT model_name, accuracy, metrics FROM model_training_logs")
        )

        instructions = []
        for row in result:
            instructions.append(
                {
                    "instruction": f"Qual a performance do modelo {row.model_name}?",
                    "context": "Resultados de Treinamento Interno - EpiScope",
                    "response": f"O modelo {row.model_name} apresenta acurácia de {row.accuracy:.2%}. {row.metrics}",
                }
            )

        with open("training_data_lora.jsonl", "w") as f:
            for entry in instructions:
                f.write(json.dumps(entry) + "\n")

    print("✅ Dataset para Fine-Tuning LoRA gerado com dados REAIS do banco!")


if __name__ == "__main__":
    generate_medical_instructions()
