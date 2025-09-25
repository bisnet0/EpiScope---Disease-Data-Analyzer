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

# --- Função de preparação dos dados (do seu run.py) ---
def prepare_data(df):
    print("\nIniciando preparação dos dados para o modelo...")
    # ATENÇÃO: Confirme se os nomes das colunas da nova API são os mesmos.
    features_relevantes = ['cs_sexo', 'cs_gestant', 'nu_idade_n', 'sg_uf_not', 'classi_fin']
    colunas_existentes = [col for col in features_relevantes if col in df.columns]
    
    if not colunas_existentes:
        raise ValueError("Nenhuma das colunas relevantes foi encontrada no DataFrame.")

    df_limpo = df[colunas_existentes].copy().dropna()

    codigos_relevantes = ['1', '2', '8'] # 1: Confirmado Laboratorial, 2: Confirmado Clínico-Epidemiológico, 8: Inconclusivo
    df_limpo['classi_fin'] = df_limpo['classi_fin'].astype(str)
    df_limpo = df_limpo[df_limpo['classi_fin'].isin(codigos_relevantes)]
    
    # Criando a variável alvo: 1 para 'Confirmado', 0 para 'Inconclusivo'
    df_limpo['alvo'] = df_limpo['classi_fin'].apply(lambda x: 1 if x in ['1', '2'] else 0)
    print(f"Registros úteis (Confirmados ou Inconclusivos): {len(df_limpo)}")
    print("Distribuição das classes:")
    print(df_limpo['alvo'].value_counts())

    if 'nu_idade_n' in df_limpo.columns:
        df_limpo['idade'] = df_limpo['nu_idade_n'].astype(str).str[1:]
        df_limpo['idade'] = pd.to_numeric(df_limpo['idade'], errors='coerce')
        df_limpo.dropna(subset=['idade'], inplace=True)
        df_limpo['idade'] = df_limpo['idade'].astype(int)

    # One-Hot Encoding para variáveis categóricas
    df_final = pd.get_dummies(df_limpo, columns=['cs_sexo', 'cs_gestant', 'sg_uf_not'], drop_first=True)

    colunas_para_remover = ['classi_fin', 'alvo']
    if 'nu_idade_n' in df_final.columns:
        colunas_para_remover.append('nu_idade_n')
        
    X = df_final.drop(columns=colunas_para_remover)
    y = df_final['alvo']
    
    print(f"Preparação concluída. Features: {X.shape[1]}, Registros: {X.shape[0]}")
    return X, y

# --- LÓGICA PRINCIPAL DE TREINAMENTO ---
if __name__ == "__main__":
    DB_USER = os.getenv("POSTGRES_USER", "bisnet0")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "RG4J8^%*TWjA*977Y40T81B2")
    DB_NAME = os.getenv("POSTGRES_DB", "episcope_db")
    DB_HOST = "db"
    DB_PORT = "5432"

    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    try:
        print("Lendo dados brutos do PostgreSQL...")
        engine = create_engine(DB_URL)
        df_bruto = pd.read_sql('SELECT * FROM raw_zika_cases', engine)
        
        X, y = prepare_data(df_bruto)

        if X.empty or y.empty or len(y.value_counts()) < 2:
            print("\nDados insuficientes para um treinamento significativo após a limpeza.")
        else:
            print('\nDividindo dados em treino e teste...')
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

            print('Treinando o modelo de Árvore de Decisão...')
            modelo = DecisionTreeClassifier(max_depth=5, random_state=42, class_weight='balanced')
            modelo.fit(X_train, y_train)

            print('Avaliando o modelo...')
            y_pred = modelo.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            relatorio = classification_report(y_test, y_pred, target_names=['Inconclusivo', 'Confirmado'], zero_division=0)

            print("\n--- Resultados da Avaliação ---")
            print(f"Acurácia: {accuracy:.2f}")
            print("\n--- Relatório de Classificação: ---")
            print(relatorio)

            # NOVO: Salvando o modelo treinado e as colunas usadas no treino
            print("\nSalvando o modelo e as colunas...")
            joblib.dump(modelo, 'decision_tree_model.joblib')
            
            # Salvar as colunas é CRUCIAL para a API saber como formatar os dados para previsão
            model_columns = list(X.columns)
            with open('model_columns.json', 'w') as f:
                json.dump(model_columns, f)
            
            print("Modelo 'decision_tree_model.joblib' e colunas 'model_columns.json' salvos com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro durante o treinamento: {e}")