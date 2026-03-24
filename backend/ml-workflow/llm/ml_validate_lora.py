import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer


def validate_assistant():
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    adapter_path = "/app/medical_assistant_adapter"

    print("🧠 Carregando inteligência especializada...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    base_model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto"
    )

    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()

    prompts = [
        "Qual a performance do modelo Glaucoma_CNN?",
        "Qual a performance do modelo XRay_CNN_Specialist?",
        "Qual a acurácia do modelo Arbovirus_DecisionTree?",
    ]
    inputs = tokenizer(f"Instruction: {prompts}\nResponse:", return_tensors="pt").to(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    for p in prompts:
        full_prompt = f"### Instruction:\n{p}\n\n### Response:\n"

        inputs = tokenizer(full_prompt, return_tensors="pt").to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

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
            print(f"🤖 Pergunta: {p}\n✅ Resposta: {clean_response}\n" + "-" * 30)


if __name__ == "__main__":
    validate_assistant()
