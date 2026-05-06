import os
from ultralytics import YOLO  # type: ignore


def train_laparoscopy_model():
    print("🚀 Iniciando treinamento do YOLOv8 para Cirurgias Laparoscópicas...")

    # 1. Carrega o modelo base "Nano" (yolov8n.pt).
    # É o mais leve e rápido, ideal para rodar sem placa de vídeo (CPU) ou para projetos acadêmicos.
    model = YOLO("yolov8n.pt")

    # Define os caminhos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(base_dir, "datasets", "laparoscopy_data", "data.yaml")

    if not os.path.exists(yaml_path):
        print(f"❌ Arquivo data.yaml não encontrado em: {yaml_path}")
        return

    # 2. Inicia o Treinamento
    # Para testes iniciais, 5 a 10 épocas são suficientes para gerar o arquivo.
    # Para a versão final da banca, você pode subir para 50.
    results = model.train(
        data=yaml_path,
        epochs=10,  # Quantas vezes ele vai estudar o material
        imgsz=640,  # Tamanho padrão da imagem
        batch=4,  # Lotes de imagens por vez (mantenha baixo se for treinar na CPU)
        name="laparo_model",  # Nome da pasta de resultados
        device="cpu",  # Mude para "0" se tiver placa de vídeo NVIDIA configurada com CUDA
    )

    print("\n✅ Treinamento Finalizado!")
    print(
        "O seu novo cérebro cirúrgico (best.pt) foi salvo na pasta 'runs/detect/laparo_model/weights/'."
    )
    print("Copie ele para a sua pasta 'models' e renomeie para 'yolo_laparoscopy.pt'!")


if __name__ == "__main__":
    train_laparoscopy_model()
