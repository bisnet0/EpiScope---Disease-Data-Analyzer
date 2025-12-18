from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

from xgboost import XGBClassifier

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

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgboost_model.joblib")
COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, "model_columns.json")
TARGET_MAP_PATH = os.path.join(ARTIFACTS_DIR, "target_map.json")
BEST_PARAMS_PATH = os.path.join(ARTIFACTS_DIR, "best_hyperparameters.json")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

try:
    print("Lendo dados da tabela 'cleaned_arboviroses_cases'...")
    try:
        with open(COLUMNS_PATH, "r") as f:
            cols_to_read = json.load(f) + ["doenca_alvo", "target_encoded"]
        print(f"Lendo apenas as colunas relevantes: {cols_to_read}")
        selected_columns_str = ", ".join([f'"{col}"' for col in cols_to_read])
        df_clean = pd.read_sql(
            f"SELECT {selected_columns_str} FROM cleaned_arboviroses_cases", engine
        )
    except FileNotFoundError:
        print("Arquivo de colunas não encontrado, lendo todas as colunas...")
        df_clean = pd.read_sql("SELECT * FROM cleaned_arboviroses_cases", engine)

    expected_features = [
        "febre",
        "mialgia",
        "cefaleia",
        "exantema",
        "vomito",
        "nausea",
        "dor_costas",
        "conjuntvit",
        "artrite",
        "artralgia",
        "petequia_n",
        "leucopenia",
        "dor_retro",
        "sexo_encoded",
        "idade",
    ]
    cols_to_keep = expected_features + ["doenca_alvo", "target_encoded"]
    df_clean = df_clean[[col for col in cols_to_keep if col in df_clean.columns]]

    print(f"Foram lidos {len(df_clean)} registros limpos e prontos para o treinamento.")

    features = [
        col for col in df_clean.columns if col not in ["doenca_alvo", "target_encoded"]
    ]
    print(f"\nModelo será treinado com {len(features)} features: {features}")

    X = df_clean[features]
    y = df_clean["target_encoded"]

    target_map = df_clean.set_index("target_encoded")["doenca_alvo"].to_dict()
    print(f"Mapa de classes alvo: {target_map}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    xgboost_params = {
        "objective": "multi:softmax",
        "num_class": len(target_map),
        "n_jobs": -1,
        "random_state": 42,
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 10,
    }

    print("\nTreinando o modelo XGBoost...")
    modelo = XGBClassifier(
        objective="multi:softmax",
        num_class=len(target_map),
        n_estimators=200,
        learning_rate=0.05,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=10,
    )
    if os.path.exists(BEST_PARAMS_PATH):
        print("Encontrados parâmetros otimizados via AG! Carregando...")
        with open(BEST_PARAMS_PATH, "r") as f:
            best_params = json.load(f)
            xgboost_params.update(best_params)
    else:
        print("Aviso: Parâmetros do AG não encontrados. Usando padrões manuais.")

    print(f"Treinando modelo com parâmetros: {xgboost_params}")

    modelo = XGBClassifier(**xgboost_params)

    eval_set = [(X_test, y_test)]
    modelo.fit(X_train, y_train, eval_set=eval_set, verbose=False)

    print("Avaliando o modelo...")
    y_pred = modelo.predict(X_test)

    report_dict = classification_report(
        y_test,
        y_pred,
        target_names=[target_map[i] for i in sorted(target_map)],
        output_dict=True,
    )

    print("\n--- Relatório de Classificação (XGBoost): ---")
    print(
        classification_report(
            y_test, y_pred, target_names=[target_map[i] for i in sorted(target_map)]
        )
    )

    importances = modelo.feature_importances_
    indices = np.argsort(importances)[::-1]

    feature_importance_list = []
    print("\n--- Importância das Features (XGBoost - Ranking): ---")
    for i in range(len(features)):
        feat_name = features[indices[i]]
        feat_score = float(importances[indices[i]])
        print(f"{i + 1}. Feature: {feat_name:<15} Importance: {feat_score:.4f}")

        feature_importance_list.append(
            {"feature": feat_name, "importance": feat_score, "rank": i + 1}
        )

    print("\nSalvando o modelo XGBoost e os artefatos no volume...")
    joblib.dump(modelo, MODEL_PATH)

    print("\nSalvando log de treinamento no banco de dados...")

    log_entry = {
        "model_name": "Arbovirus_XGBoost",
        "version": "v5",
        "parameters": json.dumps(xgboost_params),
        "feature_importance": json.dumps(feature_importance_list),
        "metrics": json.dumps(report_dict),
        "accuracy": report_dict["accuracy"],
        "dataset_size": len(df_clean),
        "created_at": pd.Timestamp.utcnow(),
    }

    try:
        log_entry_orm = {
            "model_name": "Arbovirus_XGBoost",
            "version": "v5",
            "parameters": xgboost_params,
            "feature_importance": feature_importance_list,
            "metrics": report_dict,
            "accuracy": report_dict["accuracy"],
            "dataset_size": len(df_clean),
            "created_at": datetime.now(),
        }

        insert_query = text("""
            INSERT INTO model_training_logs 
            (model_name, version, parameters, feature_importance, metrics, accuracy, dataset_size, created_at)
            VALUES (:model_name, :version, :parameters, :feature_importance, :metrics, :accuracy, :dataset_size, :created_at)
        """)

        with engine.connect() as conn:
            conn.execute(
                insert_query,
                {
                    "model_name": log_entry_orm["model_name"],
                    "version": log_entry_orm["version"],
                    "parameters": json.dumps(log_entry_orm["parameters"]),
                    "feature_importance": json.dumps(
                        log_entry_orm["feature_importance"]
                    ),
                    "metrics": json.dumps(log_entry_orm["metrics"]),
                    "accuracy": log_entry_orm["accuracy"],
                    "dataset_size": log_entry_orm["dataset_size"],
                    "created_at": log_entry_orm["created_at"],
                },
            )
            conn.commit()

        print("Log de treinamento salvo com sucesso na tabela 'model_training_logs'!")

    except Exception as e:
        print(f"AVISO: Não foi possível salvar o log no banco: {e}")

    model_columns = list(X.columns)
    with open(COLUMNS_PATH, "w") as f:
        json.dump(model_columns, f)

    with open(TARGET_MAP_PATH, "w") as f:
        json.dump(target_map, f)

    print("Modelo XGBoost e artefatos salvos com sucesso no volume!")

except Exception as e:
    print(f"Ocorreu um erro durante o treinamento: {e}")
