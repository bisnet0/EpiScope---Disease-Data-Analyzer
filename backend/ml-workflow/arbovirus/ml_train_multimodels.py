import pandas as pd
import numpy as np
import os
import json
import joblib
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("\n--- INICIANDO TREINAMENTO MULTI-MODELO (Model Zoo) ---")

# --- CONFIGURAÇÃO ---
ARTIFACTS_DIR = "/app/model_artifacts"
if not os.path.exists(ARTIFACTS_DIR): os.makedirs(ARTIFACTS_DIR)

COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, "model_columns.json")
TARGET_MAP_PATH = os.path.join(ARTIFACTS_DIR, "target_map.json")
BEST_PARAMS_PATH = os.path.join(ARTIFACTS_DIR, "best_hyperparameters.json")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

# --- 1. CARREGAMENTO DE DADOS ---
print("Carregando dados...")
try:
    with open(COLUMNS_PATH, "r") as f:
        cols_to_read = json.load(f) + ["doenca_alvo", "target_encoded"]
    cols_str = ", ".join([f'"{c}"' for c in cols_to_read])
    df = pd.read_sql(f"SELECT {cols_str} FROM cleaned_arboviroses_cases", engine)
except:
    print("AVISO: Lendo tabela completa (colunas não definidas).")
    df = pd.read_sql("SELECT * FROM cleaned_arboviroses_cases", engine)

# Features e Target
features = [c for c in df.columns if c not in ["doenca_alvo", "target_encoded"]]
X = df[features]
y = df["target_encoded"]
target_map = df.set_index("target_encoded")["doenca_alvo"].to_dict()

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"Dataset: {len(df)} linhas. Features: {len(features)}. Classes: {target_map}")

# --- 2. DEFINIÇÃO DOS MODELOS ---
models_to_train = {}

# A. Decision Tree (Simples, interpretável)
models_to_train["DecisionTree"] = DecisionTreeClassifier(max_depth=10, random_state=42)

# B. Random Forest (Robusto)
models_to_train["RandomForest"] = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)

# C. XGBoost Standard (Rápido)
models_to_train["XGBoost_Standard"] = XGBClassifier(
    objective="multi:softmax", num_class=len(target_map), 
    n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1
)

# D. XGBoost Otimizado (via Algoritmo Genético - se existir)
if os.path.exists(BEST_PARAMS_PATH):
    with open(BEST_PARAMS_PATH, 'r') as f:
        ga_params = json.load(f)
    # Garante parâmetros obrigatórios do XGB
    ga_params.update({"objective": "multi:softmax", "num_class": len(target_map), "n_jobs": -1, "random_state": 42})
    models_to_train["XGBoost_Genetic"] = XGBClassifier(**ga_params)
    print("-> Configuração do Algoritmo Genético carregada.")
else:
    print("-> AVISO: Hiperparâmetros do AG não encontrados. Pulando XGBoost_Genetic.")


# --- 3. LOOP DE TREINAMENTO E AVALIAÇÃO ---
results_summary = []

for model_name, model in models_to_train.items():
    print(f"\nTreinando: {model_name}...")
    start_time = datetime.now()
    
    # Treino
    model.fit(X_train, y_train)
    
    # Avaliação
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=[target_map[i] for i in sorted(target_map)], output_dict=True)
    
    print(f"  > Acurácia: {acc:.4f}")
    
    # Salvar Artefato
    filename = f"{model_name.lower()}.joblib"
    joblib.dump(model, os.path.join(ARTIFACTS_DIR, filename))
    
    # Feature Importance (se houver)
    feat_imp = None
    if hasattr(model, "feature_importances_"):
        feat_imp = [
            {"feature": features[i], "importance": float(model.feature_importances_[i])}
            for i in np.argsort(model.feature_importances_)[::-1]
        ]

    # --- LOG NO BANCO ---
    try:
        log_entry = {
            "model_name": f"Arbovirus_{model_name}",
            "version": "v1_multimodel",
            "parameters": json.dumps(model.get_params()).replace('NaN', 'null'),
            "feature_importance": json.dumps(feat_imp) if feat_imp else None,
            "metrics": json.dumps(report),
            "accuracy": float(acc),
            "dataset_size": len(df),
            "created_at": datetime.now()
        }
        
        insert_query = text("""
            INSERT INTO model_training_logs 
            (model_name, version, parameters, feature_importance, metrics, accuracy, dataset_size, created_at)
            VALUES (:model_name, :version, :parameters, :feature_importance, :metrics, :accuracy, :dataset_size, :created_at)
        """)
        
        with engine.connect() as conn:
            conn.execute(insert_query, log_entry)
            conn.commit()
            
    except Exception as e:
        print(f"  [Erro Log Banco]: {e}")

    results_summary.append({"model": model_name, "accuracy": acc})

# Salvar metadados comuns
with open(COLUMNS_PATH, "w") as f: json.dump(features, f)
with open(TARGET_MAP_PATH, "w") as f: json.dump(target_map, f)

print("\n--- RESUMO DO TREINAMENTO ---")
for res in sorted(results_summary, key=lambda x: x['accuracy'], reverse=True):
    print(f"{res['model']}: {res['accuracy']:.2%}")

print("\nProcesso concluído! Modelos salvos em /app/model_artifacts")