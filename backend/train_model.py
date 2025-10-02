# backend/train_model.py

import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import json

print("Iniciando o processo de treinamento do modelo...")

# 1. Conectar ao banco e carregar os dados JÁ LIMPOS
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

try:
    print("Lendo dados da tabela 'cleaned_arboviroses_cases'...")
    # A grande mudança: Lemos direto da tabela limpa!
    df_clean = pd.read_sql('SELECT * FROM cleaned_arboviroses_cases', engine)
    print(f"Foram lidos {len(df_clean)} registros limpos e prontos para o treinamento.")

    # 2. Preparar os dados para o Scikit-learn (agora é muito mais simples)
    
    # A lista de features (X) é simplesmente todas as colunas, exceto as de alvo.
    features = [col for col in df_clean.columns if col not in ['doenca_alvo', 'target_encoded']]
    print(f"\nModelo será treinado com {len(features)} features: {features}")

    X = df_clean[features]
    y = df_clean['target_encoded']
    
    # Criamos um mapa de alvos para salvar (ex: {0: 'zika', 1: 'dengue', ...})
    target_map = df_clean.set_index('target_encoded')['doenca_alvo'].to_dict()
    print(f"Mapa de classes alvo: {target_map}")
    
    # Dividimos os dados para treinar e depois validar a acurácia do modelo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # 3. Treinar o modelo
    print('\nTreinando o modelo de Árvore de Decisão...')
    # Usar class_weight='balanced' é uma boa prática para dados desbalanceados
    modelo = DecisionTreeClassifier(max_depth=10, random_state=42, class_weight='balanced')
    modelo.fit(X_train, y_train)

    # 4. Avaliar o modelo
    print('Avaliando o modelo...')
    y_pred = modelo.predict(X_test)
    
    print("\n--- Relatório de Classificação: ---")
    # Usamos as chaves do mapa como os nomes das classes para o relatório
    print(classification_report(y_test, y_pred, target_names=[target_map[i] for i in sorted(target_map)]))

    # 5. Salvar o modelo e os artefatos necessários para a predição
    print("\nSalvando o modelo e os artefatos...")
    joblib.dump(modelo, 'decision_tree_model.joblib')
    
    model_columns = list(X.columns)
    with open('model_columns.json', 'w') as f:
        json.dump(model_columns, f)

    with open('target_map.json', 'w') as f:
        json.dump(target_map, f)
    
    print("Modelo e artefatos salvos com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante o treinamento: {e}")