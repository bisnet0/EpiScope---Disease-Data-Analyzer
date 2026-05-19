import os
import cv2
import numpy as np
import shutil

# ==========================================
# 🛑 OS CAMINHOS DOS DADOS ORIGINAIS (RAW)
# ==========================================
AUTOLAPARO_IMAGES_DIR = r"C:\Users\root_\Documents\bisnet0-GitHub\EpiScope — Disease Data Analyzer\backend\modules\womens_health\datasets\autolaparo_raw\images"

AUTOLAPARO_MASKS_DIR = r"C:\Users\root_\Documents\bisnet0-GitHub\EpiScope — Disease Data Analyzer\backend\modules\womens_health\datasets\autolaparo_raw\masks"

# ==========================================
# ONDE O YOLO VAI SALVAR OS DADOS PRONTOS:
# (Ele vai gerar tudo dentro do laparoscopy_data automaticamente)
# ==========================================
YOLO_DATASET_DIR = r"C:\Users\root_\Documents\bisnet0-GitHub\EpiScope — Disease Data Analyzer\backend\modules\womens_health\datasets\laparoscopy_data"
# ==========================================

# Mapeamento das classes (Agrupando cabo e ponta da mesma ferramenta)
# Formato YOLO: 0=Grasper, 1=LigaSure, 2=Hook, 3=Uterus
CLASS_MAPPING = {
    0: [20, 40, 100, 120],  # Grasper (Instrumentos 1 e 3)
    1: [60, 80],  # LigaSure (Instrumento 2)
    2: [140, 160],  # Eletric Hook (Instrumento 4)
    3: [180],  # Útero (Anatomia)
}


def setup_directories():
    """Cria a estrutura de pastas do YOLOv8"""
    for split in ["train", "val"]:
        os.makedirs(os.path.join(YOLO_DATASET_DIR, "images", split), exist_ok=True)
        os.makedirs(os.path.join(YOLO_DATASET_DIR, "labels", split), exist_ok=True)


def create_yolo_labels():
    setup_directories()

    masks = [f for f in os.listdir(AUTOLAPARO_MASKS_DIR) if f.endswith(".png")]
    total = len(masks)

    print(f"🔄 Iniciando conversão de {total} máscaras para o formato YOLO...")

    for idx, mask_filename in enumerate(masks):
        mask_path = os.path.join(AUTOLAPARO_MASKS_DIR, mask_filename)
        # O README diz que o nome da imagem original é igual, mas com .jpg
        img_filename = mask_filename.replace(".png", ".jpg")
        img_path = os.path.join(AUTOLAPARO_IMAGES_DIR, img_filename)

        if not os.path.exists(img_path):
            continue

        # Regra de Separação do README (001 a 170 = Train | 171 a 227 = Val)
        video_id = int(mask_filename[:3])
        split = "train" if video_id <= 170 else "val"
        if video_id > 227:  # Ignora o test set para economizar tempo agora
            continue

        # Lê a máscara em preto e branco
        mask_data = np.fromfile(mask_path, dtype=np.uint8)
        mask = cv2.imdecode(mask_data, cv2.IMREAD_GRAYSCALE)

        # 👇 A trava para acalmar o Pylance (Se der erro de leitura, pula pra próxima)
        if mask is None:
            print(
                f"⚠️ Aviso: Não foi possível ler a máscara {mask_filename}. Pulando..."
            )
            continue

        h, w = mask.shape

        yolo_annotations = []

        # Procura os pixels de cada classe
        for class_id, pixel_values in CLASS_MAPPING.items():
            # Cria uma máscara binária (tudo que for dessa ferramenta vira 1, o resto 0)
            binary_mask = np.isin(mask, pixel_values).astype(np.uint8)

            # Encontra os contornos (bordas) da ferramenta
            contours, _ = cv2.findContours(
                binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            for cnt in contours:
                if cv2.contourArea(cnt) < 100:  # Ignora ruídos muito pequenos
                    continue

                # Pega o quadrado ao redor do contorno
                x, y, box_w, box_h = cv2.boundingRect(cnt)

                # Converte para o padrão YOLO (Centro X, Centro Y, Largura, Altura normalizados)
                x_center = (x + box_w / 2) / w
                y_center = (y + box_h / 2) / h
                norm_w = box_w / w
                norm_h = box_h / h

                yolo_annotations.append(
                    f"{class_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}"
                )

        # Se achou alguma coisa na tela, salva a imagem e o .txt
        if yolo_annotations:
            # Salva o arquivo .txt
            txt_filename = mask_filename.replace(".png", ".txt")
            txt_path = os.path.join(YOLO_DATASET_DIR, "labels", split, txt_filename)
            with open(txt_path, "w") as f:
                f.write("\n".join(yolo_annotations))

            # Copia a imagem colorida
            shutil.copy(
                img_path, os.path.join(YOLO_DATASET_DIR, "images", split, img_filename)
            )

        if (idx + 1) % 100 == 0:
            print(f"Progresso: {idx + 1}/{total} processados...")

    print("✅ Conversão concluída! O Dataset está pronto para o YOLOv8.")


if __name__ == "__main__":
    create_yolo_labels()
