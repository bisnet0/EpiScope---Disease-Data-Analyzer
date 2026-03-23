import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
import json


def prepare_medical_dataset():

    data = [
        {
            "instruction": "Como o EpiScope diagnostica Arboviroses?",
            "context": "Log de Treino v1_multimodel",
            "response": "O EpiScope utiliza um ensemble de XGBoost e Random Forest com acurácia de 98%, validado por algoritmos genéticos.",
        },
        {
            "instruction": "Qual o protocolo para detecção de Glaucoma no EpiScope?",
            "context": "Modelo MobileNetV2_FT",
            "response": "Utilizamos transfer learning sobre MobileNetV2 com fine-tuning nas últimas 100 camadas para identificar escavação do disco óptico.",
        },
        {
            "instruction": "Como o EpiScope detecta Pneumonia em imagens de Raio-X?",
            "context": "Pipeline Chest X-Ray v2 (CNN)",
            "response": "O diagnóstico de Pneumonia é realizado através de uma Rede Neural Convolucional (CNN) otimizada para identificar infiltrados alveolares e opacidades pulmonares com alta sensibilidade.",
        },
        {
            "instruction": "Qual a conduta do Maestro para exames de Raio-X com alta probabilidade de pneumonia?",
            "context": "Protocolo de Emergência Pulmonar",
            "response": "O Maestro aciona o protocolo de severidade HIGH, sugere avaliação imediata de sinais vitais (CURB-65) e abre o chat de suporte à decisão clínica.",
        },
    ]
    return Dataset.from_list(data)


def run_fine_tuning():
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto"
    )

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)

    print("✅ Pipeline de Fine-Tuning (LoRA) configurado com sucesso.")
    model.save_pretrained("./medical_assistant_adapter")


if __name__ == "__main__":
    run_fine_tuning()
