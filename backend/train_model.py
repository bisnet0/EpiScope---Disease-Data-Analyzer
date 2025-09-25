# backend/train_model.py

import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from dotenv import load_dotenv
import json

load_dotenv()

# MUDANÇA SIGNIFICATIVA: Nova função de preparação de dados
def prepare_data(df):
    print("\nIniciando preparação dos dados para o modelo multiclasse...")

    # NOVO: Lista unificada de features (sintomas + demográficos)
    # Verificamos quais colunas existem no dataframe combinado
    sintomas_comuns = [
        'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea', 
        'dor_costas', 'conjuntvit', 'artrite', 'artralgia', 'petequia_n', 
        'leucopenia', 'dor_retro'
    ]
    features_demograficas = ['cs_sexo', 'nu_idade_n']
    
    colunas_sintomas_existentes = [col for col in sintomas_comuns if col in df.columns]
    colunas_demo_existentes = [col for col in features_demograficas if col in df.columns]
    
    features_usadas = colunas_sintomas_existentes + colunas_demo_existentes
    print(f"Features que serão usadas: {features_usadas}")

    df_limpo = df[features_usadas + ['doenca_alvo']].copy().dropna(subset=['doenca_alvo'])

    # 1. Limpeza dos Sintomas: Converter '1'(Sim) para 1, e outros (Não, Ignorado, Null) para 0
    for col in colunas_sintomas_existentes:
        df_limpo[col] = df_limpo[col].apply(lambda x: 1 if str(x).strip() == '1' else 0)

    # 2. Limpeza de Idade
    if 'nu_idade_n' in df_limpo.columns:
        df_limpo['idade'] = df_limpo['nu_idade_n'].astype(str).str.slice(1).replace('', '0').astype(int)
        df_limpo = df_limpo.drop(columns=['nu_idade_n'])

    # 3. One-Hot Encoding para 'cs_sexo'
    if 'cs_sexo' in df_limpo.columns:
        df_limpo = pd.get_dummies(df_limpo, columns=['cs_sexo'], drop_first=True)

    # 4. Criar a variável alvo (y) e o mapa de classes
    df_limpo['target'] = df_limpo['doenca_alvo'].astype('category').cat.codes
    target_map = dict(enumerate(df_limpo['doenca_alvo'].astype('category').cat.categories))
    print(f"\nMapa de classes alvo: {target_map}")

    X = df_limpo.drop(columns=['doenca_alvo', 'target'])
    y = df_limpo['target']

    # Garantir que todas as colunas de features sejam numéricas
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

    print(f"Preparação concluída. Features: {X.shape[1]}, Registros: {X.shape[0]}")
    return X, y, target_map

if __name__ == "__main__":
    DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    
    try:
        print("Lendo dados combinados do PostgreSQL...")
        engine = create_engine(DB_URL)
        df_bruto = pd.read_sql('SELECT * FROM raw_arboviroses_cases', engine)

        X, y, target_map = prepare_data(df_bruto)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        
        print('\nTreinando o modelo de Árvore de Decisão multiclasse...')
        modelo = DecisionTreeClassifier(max_depth=10, random_state=42, class_weight='balanced')
        modelo.fit(X_train, y_train)

        print('Avaliando o modelo...')
        y_pred = modelo.predict(X_test)
        report_dict = classification_report(y_test, y_pred, target_names=target_map.values(), output_dict=True)
        
        print("\n--- Resultados da Avaliação ---")
        print(f"Acurácia: {report_dict['accuracy']:.2f}")
        print("\n--- Relatório de Classificação: ---")
        print(classification_report(y_test, y_pred, target_names=target_map.values()))

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