import os
import json
import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer

# ==========================================
# 📂 CONFIGURAÇÃO DE DIRETÓRIOS E CAMINHOS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")
os.makedirs(TRAIN_RESULTS_DIR, exist_ok=True)

ADAPTER_SAVE_PATH = os.path.join(TRAIN_RESULTS_DIR, "medical_assistant_adapter")
DATASET_PATH = os.path.join(TRAIN_RESULTS_DIR, "training_data_lora.jsonl")

def prepare_medical_dataset():
    # Dados base fixos para o Maestro
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

    # Tenta carregar o dataset dinâmico gerado pelo script anterior
    if os.path.exists(DATASET_PATH):
        print(f"📖 Carregando dados adicionais do banco de: {DATASET_PATH}")
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))

    print(f"📊 Dataset final contém {len(data)} instruções para fine-tuning.")
    return Dataset.from_list(data)

def run_fine_tuning():
    print("🤖 Iniciando configuração do LLM Médico...")
    
    # Preparando os dados
    dataset = prepare_medical_dataset()

    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # Adicionando o pad_token se não existir (necessário para treinamento)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

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

    # Aqui no futuro você pode colocar o Trainer(...) chamando model.fit() ou trainer.train()
    # Por enquanto, estamos apenas salvando a arquitetura configurada do PEFT

    print("✅ Pipeline de Fine-Tuning (LoRA) configurado com sucesso.")
    model.save_pretrained(ADAPTER_SAVE_PATH)
    print(f"💾 Adaptador LoRA salvo em: {ADAPTER_SAVE_PATH}")

if __name__ == "__main__":
    run_fine_tuning()