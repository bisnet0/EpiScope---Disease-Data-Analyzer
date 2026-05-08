import os
from ultralytics import YOLO  # type: ignore

# Pega a pasta onde este script está (ml-workflow)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Aponta para o YAML que acabamos de criar
YAML_PATH = os.path.join(SCRIPT_DIR, "..", "datasets", "laparoscopy_data", "data.yaml")


def train_laparoscopy_model():
    print("🚀 Iniciando treinamento do YOLOv8 para Cirurgias Laparoscópicas...")

    # Baixa a rede neural convolucional YOLOv8 "Nano" (leve e rápida)
    model = YOLO("yolov8n.pt")

    if not os.path.exists(YAML_PATH):
        print(f"❌ Erro: Arquivo data.yaml não encontrado em: {YAML_PATH}")
        return

    # Inicia o Treinamento
    print(f"📄 Lendo configurações do dataset em: {YAML_PATH}")
    results = model.train(
        data=YAML_PATH,
        epochs=5,  # 👇 Coloquei apenas 5 épocas para você ver o resultado rápido hoje! Depois para a banca você pode por 30 ou 50.
        imgsz=640,  # Tamanho padrão que a IA enxerga
        batch=4,  # Quantas imagens ele estuda de uma vez
        name="laparo_model",
        device="cpu",  # Se você tiver uma placa de vídeo da NVIDIA configurada, mude para 0
    )

    print("\n✅ Treinamento Finalizado com Sucesso!")
    print(
        "O seu modelo treinado (best.pt) foi salvo na pasta 'runs/detect/laparo_model/weights/'."
    )


if __name__ == "__main__":
    train_laparoscopy_model()
