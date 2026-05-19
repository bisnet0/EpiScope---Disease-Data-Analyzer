import warnings
warnings.filterwarnings('ignore')
import os
import gc
import librosa # type: ignore
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "datasets", "audio")
CSV_FEATURES_PATH = os.path.join(BASE_DIR, "..", "datasets", "audio_features.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "models", "audio_distress_model.pkl")
SCALER_OUTPUT_PATH = os.path.join(BASE_DIR, "..", "models", "audio_scaler.pkl")

# Mapeamento do CREMA-D para o nosso caso de uso
EMOTION_MAP = {
    'ANG': 1, 'DIS': 1, 'FEA': 1, 'SAD': 1, # Risco / Distress
    'HAP': 0, 'NEU': 0                      # Normal / Estável
}


def extract_audio_features(file_path):
    try:
        # VOLTAMOS AO NORMAL: Passando a string do caminho direto pro Librosa
        y, sr = librosa.load(file_path, sr=22050, duration=3.0) 
        
        if len(y) == 0:
            return None

        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        rms = librosa.feature.rms(y=y)
        
        features = np.hstack((np.mean(mfccs.T, axis=0), np.mean(rms)))
        return features
    except Exception as e:
        filename = os.path.basename(file_path)
        print(f"⚠️ Pulo: {filename} ({str(e)})")
        return None

def build_incremental_dataset():
    if os.path.exists(CSV_FEATURES_PATH):
        print("✅ CSV de áudio já existe. Pulando extração para ir direto ao treino!")
        return True

    print("⏳ Iniciando extração de features de áudio em chunks...")
    files = [f for f in os.listdir(DATASET_PATH) if f.endswith('.wav')]
    total = len(files)
    
    with open(CSV_FEATURES_PATH, 'w') as f:
        # Escreve o cabeçalho do CSV
        cols = [f"mfcc_{i}" for i in range(13)] + ["rms", "label"]
        f.write(",".join(cols) + "\n")

        for idx, filename in enumerate(files):
            # Extrai o label do nome (Ex: 1001_DFA_ANG_XX.wav -> ANG)
            parts = filename.split('_')
            if len(parts) < 3: continue
            
            emotion_code = parts[2]
            label = EMOTION_MAP.get(emotion_code)
            if label is None: continue

            file_path = os.path.join(DATASET_PATH, filename)
            features = extract_audio_features(file_path)

            if features is not None:
                # Salva linha a linha no CSV (Evita Memory Leak)
                row = np.append(features, label)
                f.write(",".join(map(str, row)) + "\n")

            # A cada 100 arquivos, limpa o lixo da memória
            if (idx + 1) % 100 == 0:
                print(f"Progresso Áudio: {idx + 1}/{total} processados...")
                gc.collect()

    print("✅ Extração de áudio concluída!")
    return True

def train_model():
    build_incremental_dataset()
    
    print("🧠 Carregando CSV e treinando Random Forest...")
    df = pd.read_csv(CSV_FEATURES_PATH)
    X = df.drop(columns=['label'])
    y = df['label']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\n📊 Relatório de Áudio:")
    print(classification_report(y_test, y_pred, target_names=["Estável", "Risco"]))

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)
    joblib.dump(scaler, SCALER_OUTPUT_PATH)
    print("✅ Modelo salvo com sucesso!")

if __name__ == "__main__":
    train_model()