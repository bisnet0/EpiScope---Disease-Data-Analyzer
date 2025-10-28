# backend/train_cnn_glaucoma.py (Adapted for Drishti-GS)

import os
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder # Use LabelEncoder for binary
import json
import time

print("Iniciando script de treinamento da CNN para Glaucoma (Drishti-GS)...")
start_time = time.time()

# --- Configurações ---
DATASET_DIR = "/app/data/drishti_gs" # Path inside the container
METADATA_FILE = os.path.join(DATASET_DIR, "Drishti-GS1_files_info.xlsx") # Path to the Excel label file
IMAGE_DIR = os.path.join(DATASET_DIR, "Training", "Images") # Path to training images

ARTIFACTS_DIR = "/app/model_artifacts"
MODEL_SAVE_PATH = os.path.join(ARTIFACTS_DIR, 'glaucoma_cnn_model.h5')
INFO_SAVE_PATH = os.path.join(ARTIFACTS_DIR, 'glaucoma_info.json')

IMG_SIZE = 224
BATCH_SIZE = 16 # Smaller batch size might be better for smaller datasets
EPOCHS = 30 # Increased epochs slightly
LEARNING_RATE = 0.001
TEST_SPLIT_SIZE = 0.2 # 20% for validation

# --- Funções Auxiliares ---

def preprocess_image(image_path, target_size=(IMG_SIZE, IMG_SIZE)):
    """Carrega, redimensiona e normaliza uma imagem."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Aviso: Não foi possível ler a imagem: {image_path}")
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, target_size)
        img_normalized = img_resized / 255.0
        return img_normalized
    except Exception as e:
        print(f"Erro ao processar imagem {image_path}: {e}")
        return None

def load_data_from_excel(metadata_path, image_dir):
    """Carrega imagens e labels usando o arquivo Excel Drishti-GS."""
    print(f"Carregando metadados de: {metadata_path}")
    try:
        # Try reading as Excel first, then CSV as fallback
        try:
            df = pd.read_excel(metadata_path)
        except ValueError: # If it's actually a CSV saved as .xlsx
             df = pd.read_csv(metadata_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de metadados não encontrado em {metadata_path}. Verifique o caminho.")

    print(f"Metadados carregados. Colunas: {df.columns.tolist()}")

    # --- Ajuste as colunas com base no seu arquivo Excel real ---
    filename_col = 'Drishti-GS File' # Coluna com nomes como 'drishtiGS_001''
    label_col = 'Total'             # Coluna com 'Normal' ou 'Glaucomatous'
    # -------------------------------------------------------------------

    if filename_col not in df.columns or label_col not in df.columns:
        raise ValueError(f"Colunas '{filename_col}' ou '{label_col}' não encontradas no arquivo de metadados.")

    images = []
    labels = []
    class_names = sorted(df[label_col].unique().tolist())
    print(f"Classes encontradas nos metadados: {class_names}")

    missing_files = 0
    for index, row in df.iterrows():
        # Limpa o nome do arquivo (ex: remove ' se houver) e adiciona extensão
        base_filename = str(row[filename_col]).strip().replace("'", "")
        img_filename = f"{base_filename}.png" # Assume extensão .png
        img_path = os.path.join(image_dir, img_filename)

        if not os.path.exists(img_path):
            print(f"Aviso: Arquivo de imagem não encontrado: {img_path}")
            missing_files += 1
            continue # Pula esta imagem se não existir

        processed_img = preprocess_image(img_path)
        if processed_img is not None:
            images.append(processed_img)
            labels.append(row[label_col]) # Guarda o label 'Normal' ou 'Glaucomatous'

    if missing_files > 0:
        print(f"AVISO: {missing_files} arquivos de imagem listados nos metadados não foram encontrados.")
    if not images:
         raise ValueError("Nenhuma imagem válida foi carregada. Verifique os caminhos e formatos.")

    print(f"Total de imagens carregadas: {len(images)}")
    return np.array(images), np.array(labels), class_names

# --- Script Principal ---
try:
    # 1. Carregar Dados
    images, labels, class_names = load_data_from_excel(METADATA_FILE, IMAGE_DIR)

    # 2. Codificar Labels (Binary: 0 or 1)
    print("Codificando labels (Normal=0, Glaucomatous=1)...")
    label_encoder = LabelEncoder()
    # Garante que 'Normal' seja 0 e 'Glaucomatous' seja 1 (ou a outra classe)
    label_encoder.fit(['Normal', 'Glaucomatous']) # Fit com as classes esperadas
    encoded_labels = label_encoder.transform(labels)

    num_classes = len(class_names)
    if num_classes != 2:
        print(f"Aviso: Esperado 2 classes (Normal, Glaucomatous), mas {num_classes} foram encontradas: {class_names}. Usando classificação binária.")

    print(f"Labels codificados.")

    # 3. Dividir em Treino e Validação
    print("Dividindo dados em treino e validação...")
    X_train, X_val, y_train, y_val = train_test_split(
        images, encoded_labels, test_size=TEST_SPLIT_SIZE, random_state=42, stratify=encoded_labels
    )
    print(f"Tamanho do treino: {len(X_train)}, Tamanho da validação: {len(X_val)}")

    # 4. Data Augmentation
    train_datagen = ImageDataGenerator(
        rotation_range=15, width_shift_range=0.1, height_shift_range=0.1,
        shear_range=0.1, zoom_range=0.1, horizontal_flip=True, fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator() # No augmentation for validation

    train_generator = train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE)
    val_generator = val_datagen.flow(X_val, y_val, batch_size=BATCH_SIZE)

    # 5. Construir o Modelo (Transfer Learning - Binary Classification)
    print("Construindo o modelo CNN (Transfer Learning - Binário)...")
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    # --- MUDANÇA: Camada final para classificação binária ---
    predictions = Dense(1, activation='sigmoid')(x)
    # --- FIM DA MUDANÇA ---

    model = Model(inputs=base_model.input, outputs=predictions)

    # 6. Compilar o Modelo (Binary Classification)
    print("Compilando o modelo...")
    optimizer = Adam(learning_rate=LEARNING_RATE)
    # --- MUDANÇA: Loss para classificação binária ---
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    # --- FIM DA MUDANÇA ---

    model.summary()

    # 7. Treinar o Modelo
    print(f"Iniciando treinamento por {EPOCHS} épocas...")
    # Add EarlyStopping callback
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    history = model.fit(
        train_generator,
        steps_per_epoch=max(1, len(X_train) // BATCH_SIZE), # Garante pelo menos 1 step
        epochs=EPOCHS,
        validation_data=val_generator,
        validation_steps=max(1, len(X_val) // BATCH_SIZE), # Garante pelo menos 1 step
        callbacks=[early_stopping] # Adiciona early stopping
    )

    # 8. Avaliar
    print("Avaliando o modelo final no conjunto de validação...")
    loss, accuracy = model.evaluate(val_generator, steps=max(1, len(X_val) // BATCH_SIZE))
    print(f"Acurácia final na validação: {accuracy:.4f}")

    # 9. Salvar Modelo e Informações
    print(f"Salvando modelo treinado em: {MODEL_SAVE_PATH}")
    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)
    model.save(MODEL_SAVE_PATH)

    model_info = {
        "image_size": IMG_SIZE,
        "class_names": class_names, # Deve ser ['Normal', 'Glaucomatous']
        "label_encoding": label_encoder.classes_.tolist() # Ex: ['Normal', 'Glaucomatous']
    }
    print(f"Salvando informações do modelo em: {INFO_SAVE_PATH}")
    with open(INFO_SAVE_PATH, 'w') as f:
        json.dump(model_info, f)

    end_time = time.time()
    print(f"Treinamento concluído em {end_time - start_time:.2f} segundos.")

except Exception as e:
    print(f"Ocorreu um erro durante o treinamento da CNN: {e}")
    import traceback
    traceback.print_exc() # Imprime o traceback completo para debug