# backend/train_model.py (V5 - XGBoost)

import pandas as pd
from sqlalchemy import create_engine
# --- MUDANÇA: Importar XGBoost ---
from xgboost import XGBClassifier
# --- FIM DA MUDANÇA ---
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os
import json
import numpy as np

print("Iniciando o processo de treinamento do modelo (V5 - XGBoost)...")

ARTIFACTS_DIR = "/app/model_artifacts"
if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR)

# --- MUDANÇA: Nome do arquivo do modelo (opcional, mas bom) ---
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'xgboost_model.joblib')
# --- FIM DA MUDANÇA ---
COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, 'model_columns.json')
TARGET_MAP_PATH = os.path.join(ARTIFACTS_DIR, 'target_map.json')

# 1. Conectar e carregar dados
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

try:
    print("Lendo dados da tabela 'cleaned_arboviroses_cases'...")
    try:
        with open(COLUMNS_PATH, 'r') as f:
             cols_to_read = json.load(f) + ['doenca_alvo', 'target_encoded']
        print(f"Lendo apenas as colunas relevantes: {cols_to_read}")
        selected_columns_str = ', '.join([f'"{col}"' for col in cols_to_read])
        df_clean = pd.read_sql(f'SELECT {selected_columns_str} FROM cleaned_arboviroses_cases', engine)
    except FileNotFoundError:
        print("Arquivo de colunas não encontrado, lendo todas as colunas...")
        df_clean = pd.read_sql('SELECT * FROM cleaned_arboviroses_cases', engine)
    # Garante que não lemos colunas extras se o arquivo JSON não existia
    expected_features = [
        'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea', 
        'dor_costas', 'conjuntvit', 'artrite', 'artralgia', 'petequia_n', 
        'leucopenia', 'dor_retro', 'sexo_encoded', 'idade'
    ]
    cols_to_keep = expected_features + ['doenca_alvo', 'target_encoded']
    df_clean = df_clean[[col for col in cols_to_keep if col in df_clean.columns]]

    print(f"Foram lidos {len(df_clean)} registros limpos e prontos para o treinamento.")

    # 2. Preparar os dados
    features = [col for col in df_clean.columns if col not in ['doenca_alvo', 'target_encoded']]
    print(f"\nModelo será treinado com {len(features)} features: {features}")

    X = df_clean[features]
    y = df_clean['target_encoded']

    target_map = df_clean.set_index('target_encoded')['doenca_alvo'].to_dict()
    print(f"Mapa de classes alvo: {target_map}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # 3. Treinar o modelo
    print('\nTreinando o modelo XGBoost...')
    # --- MUDANÇA: Usar XGBClassifier ---
    # Parâmetros básicos. `enable_categorical=True` pode ajudar se tivermos features categóricas no futuro.
    # `objective='multi:softmax'` para classificação multiclasse. `num_class=3` para nossas 3 doenças.
    modelo = XGBClassifier(objective='multi:softmax', num_class=len(target_map),
                           n_estimators=200,      # Mais árvores
                           learning_rate=0.05,    # Aprendizado mais lento
                           max_depth=10,          # Árvores mais profundas
                           random_state=42,
                           n_jobs=-1,
                           early_stopping_rounds=10
                          )
    
    # XGBoost usa o conjunto de teste para early stopping
    eval_set = [(X_test, y_test)]
    modelo.fit(X_train, y_train, eval_set=eval_set, verbose=False) # verbose=False para não poluir o log
    # --- FIM DA MUDANÇA ---

    # 4. Avaliar o modelo
    print('Avaliando o modelo...')
    y_pred = modelo.predict(X_test) # predict_proba também existe se precisar das probs

    print("\n--- Relatório de Classificação (XGBoost): ---")
    print(classification_report(y_test, y_pred, target_names=[target_map[i] for i in sorted(target_map)]))

    # Imprimir Feature Importances (XGBoost também tem)
    print("\n--- Importância das Features (XGBoost - Ranking): ---")
    importances = modelo.feature_importances_
    indices = np.argsort(importances)[::-1]

    for i in range(len(features)):
        print(f"{i + 1}. Feature: {features[indices[i]]:<15} Importance: {importances[indices[i]]:.4f}")

    # 5. Salvar o modelo e os artefatos
    print("\nSalvando o modelo XGBoost e os artefatos no volume...")
    joblib.dump(modelo, MODEL_PATH) # Salva no novo caminho xgboost_model.joblib

    model_columns = list(X.columns) # Salva as 15 colunas usadas
    with open(COLUMNS_PATH, 'w') as f:
        json.dump(model_columns, f)

    with open(TARGET_MAP_PATH, 'w') as f:
        json.dump(target_map, f)

    print("Modelo XGBoost e artefatos salvos com sucesso no volume!")

except Exception as e:
    print(f"Ocorreu um erro durante o treinamento: {e}")