# backend/train_cnn_glaucoma.py (V2 - Com Fine-Tuning)

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
from sklearn.preprocessing import LabelEncoder
import json
import time

print("Iniciando script de treinamento da CNN (V2 - Fine-Tuning)...")
start_time = time.time()

# --- Configurações ---
DATASET_DIR = "/app/data/drishti_gs"
METADATA_FILE = os.path.join(DATASET_DIR, "Drishti-GS1_diagnosis.xlsx")
IMAGE_DIR = os.path.join(DATASET_DIR, "Training", "Images")

ARTIFACTS_DIR = "/app/model_artifacts"
MODEL_SAVE_PATH = os.path.join(ARTIFACTS_DIR, 'glaucoma_cnn_model.h5')
INFO_SAVE_PATH = os.path.join(ARTIFACTS_DIR, 'glaucoma_info.json')

IMG_SIZE = 224
BATCH_SIZE = 16 
INITIAL_EPOCHS = 20 # Épocas para treinar SÓ o topo
FINE_TUNE_EPOCHS = 20 # Épocas para treinar o modelo todo (total 40)
LEARNING_RATE = 0.001
FINE_TUNE_LR = 0.00001 # Taxa de aprendizado 100x menor
TEST_SPLIT_SIZE = 0.2

# --- Funções Auxiliares (Idênticas) ---
def preprocess_image(image_path, target_size=(IMG_SIZE, IMG_SIZE)):
    try:
        img = cv2.imread(image_path)
        if img is None: return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, target_size)
        img_normalized = img_resized / 255.0
        return img_normalized
    except Exception as e:
        print(f"Erro processando {image_path}: {e}")
        return None

def load_data_from_excel(metadata_path, image_dir):
    print(f"Carregando metadados de: {metadata_path}")
    try:
        try: df = pd.read_excel(metadata_path)
        except ValueError: df = pd.read_csv(metadata_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de metadados não encontrado em {metadata_path}.")
    
    filename_col = 'Drishti-GS File'; label_col = 'Total'
    if filename_col not in df.columns or label_col not in df.columns:
        raise ValueError(f"Colunas '{filename_col}' ou '{label_col}' não encontradas.")

    images = []; labels = []; class_names = sorted(df[label_col].unique().tolist())
    print(f"Classes encontradas: {class_names}")

    for index, row in df.iterrows():
        base_filename = str(row[filename_col]).strip().replace("'", "")
        img_filename = f"{base_filename}.png" 
        img_path = os.path.join(image_dir, img_filename)

        if not os.path.exists(img_path):
            # Tenta .jpg como fallback
            img_filename = f"{base_filename}.jpg"
            img_path = os.path.join(image_dir, img_filename)
            if not os.path.exists(img_path):
                print(f"Aviso: Arquivo de imagem não encontrado (tentou .png e .jpg): {base_filename}")
                continue

        processed_img = preprocess_image(img_path)
        if processed_img is not None:
            images.append(processed_img)
            labels.append(row[label_col])

    print(f"Total de imagens carregadas: {len(images)}")
    return np.array(images), np.array(labels), class_names

# --- Script Principal ---
try:
    # 1. Carregar Dados
    images, labels, class_names = load_data_from_excel(METADATA_FILE, IMAGE_DIR)

    # 2. Codificar Labels (Binary: Glaucomatous=0, Normal=1)
    print("Codificando labels (Glaucomatous=0, Normal=1)...")
    label_encoder = LabelEncoder()
    # LabelEncoder.fit() ordena alfabeticamente. 
    # 'Glaucomatous' vem antes de 'Normal'.
    label_encoder.fit(labels) 
    # ['Glaucomatous', 'Normal'] -> [0, 1]
    encoded_labels = label_encoder.transform(labels)
    
    print(f"Labels codificados. Mapeamento: {list(label_encoder.classes_)}") # Deve mostrar ['Glaucomatous', 'Normal']

    # 3. Dividir Dados
    X_train, X_val, y_train, y_val = train_test_split(
        images, encoded_labels, test_size=TEST_SPLIT_SIZE, random_state=42, stratify=encoded_labels
    )
    print(f"Tamanho do treino: {len(X_train)}, Tamanho da validação: {len(X_val)}")

    # 4. Data Augmentation
    train_datagen = ImageDataGenerator(
        rotation_range=30, width_shift_range=0.15, height_shift_range=0.15,
        shear_range=0.15, zoom_range=0.15, horizontal_flip=True, fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator()
    train_generator = train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE)
    val_generator = val_datagen.flow(X_val, y_val, batch_size=BATCH_SIZE)

    # 5. Construir o Modelo
    print("Construindo o modelo CNN...")
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base_model.trainable = False # Congela a base por enquanto

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation='sigmoid')(x) # Sigmoid para binário (prob de classe 1, ou seja, 'Normal')
    model = Model(inputs=base_model.input, outputs=predictions)

    # 6. Compilar o Modelo (Fase 1)
    print("Compilando o modelo (Fase 1)...")
    optimizer = Adam(learning_rate=LEARNING_RATE)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()

    # 7. Treinar o Modelo (Fase 1 - Só o Topo)
    print(f"Iniciando treinamento (Fase 1 - Topo) por {INITIAL_EPOCHS} épocas...")
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    history = model.fit(
        train_generator,
        steps_per_epoch=max(1, len(X_train) // BATCH_SIZE),
        epochs=INITIAL_EPOCHS,
        validation_data=val_generator,
        validation_steps=max(1, len(X_val) // BATCH_SIZE),
        callbacks=[early_stopping]
    )
    
    print("Fase 1 concluída. Descongelando camadas para Fine-Tuning...")

    # 8. Fine-Tuning (Fase 2 - Descongelar e Treinar)
    base_model.trainable = True # Descongela o modelo base
    
    # Vamos congelar as primeiras camadas e treinar só o final
    fine_tune_at = 100 # Congela as primeiras 100 camadas
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    # Re-compilar com uma taxa de aprendizado muito baixa
    print("Re-compilando modelo para Fine-Tuning...")
    optimizer_fine_tune = Adam(learning_rate=FINE_TUNE_LR)
    model.compile(optimizer=optimizer_fine_tune, loss='binary_crossentropy', metrics=['accuracy'])
    
    model.summary() # Mostra os novos parâmetros treináveis

    print(f"Iniciando treinamento (Fase 2 - Fine-Tuning) por mais {FINE_TUNE_EPOCHS} épocas...")
    history_fine_tune = model.fit(
        train_generator,
        steps_per_epoch=max(1, len(X_train) // BATCH_SIZE),
        epochs=INITIAL_EPOCHS + FINE_TUNE_EPOCHS, # Continua de onde parou
        initial_epoch=history.epoch[-1], # Começa da última época da Fase 1
        validation_data=val_generator,
        validation_steps=max(1, len(X_val) // BATCH_SIZE),
        callbacks=[early_stopping] # Reutiliza o early stopping
    )

    # 9. Avaliar
    print("Avaliando o modelo final (pós Fine-Tuning)...")
    loss, accuracy = model.evaluate(val_generator, steps=max(1, len(X_val) // BATCH_SIZE))
    print(f"Acurácia final na validação: {accuracy:.4f}")

    # 10. Salvar
    print(f"Salvando modelo treinado em: {MODEL_SAVE_PATH}")
    if not os.path.exists(ARTIFACTS_DIR): os.makedirs(ARTIFACTS_DIR)
    model.save(MODEL_SAVE_PATH)
    
    model_info = {
        "image_size": IMG_SIZE,
        "class_names": label_encoder.classes_.tolist() # Salva o mapeamento ['Glaucomatous', 'Normal']
    }
    print(f"Salvando informações do modelo em: {INFO_SAVE_PATH}")
    with open(INFO_SAVE_PATH, 'w') as f:
        json.dump(model_info, f)

    end_time = time.time()
    print(f"Treinamento concluído em {end_time - start_time:.2f} segundos.")

except Exception as e:
    print(f"Ocorreu um erro durante o treinamento da CNN: {e}")
    import traceback
    traceback.print_exc()