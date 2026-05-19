import os
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# ==========================================
# 📂 CONFIGURAÇÃO DE DIRETÓRIOS E CAMINHOS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")

# Apontando para o adaptador salvo pelo script de treinamento
ADAPTER_PATH = os.path.join(TRAIN_RESULTS_DIR, "medical_assistant_adapter")

def validate_assistant():
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    print(f"🧠 Carregando inteligência especializada de: {ADAPTER_PATH}...")
    
    if not os.path.exists(ADAPTER_PATH):
        print(f"❌ Erro: Adaptador não encontrado em {ADAPTER_PATH}.")
        print("Execute o script ml_train_medical_assistant.py primeiro!")
        return

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    base_model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto"
    )

    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()

    prompts = [
        "Qual a performance do modelo Glaucoma_CNN?",
        "Qual a performance do modelo XRay_CNN_Specialist?",
        "Qual a acurácia do modelo Arbovirus_DecisionTree?",
    ]
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚡ Rodando inferência no dispositivo: {device.upper()}\n" + "="*40)

    for p in prompts:
        full_prompt = f"### Instruction:\n{p}\n\n### Response:\n"

        inputs = tokenizer(full_prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
            )

            response = tokenizer.decode(outputs[0], skip_special_tokens=True)

            clean_response = response.split("### Response:")[-1].strip()
            print(f"🤖 Pergunta: {p}\n✅ Resposta: {clean_response}\n" + "-" * 40)

if __name__ == "__main__":
    validate_assistant()