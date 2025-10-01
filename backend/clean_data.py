# backend/clean_data.py

import pandas as pd
from sqlalchemy import create_engine
import os

print("Iniciando processo de limpeza e transformação de dados...")

# 1. Conectar ao banco de dados
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = "db"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DB_URL)

try:
    # 2. Ler os dados da tabela crua
    print("Lendo dados da tabela 'raw_arboviroses_cases'...")
    df_raw = pd.read_sql('SELECT * FROM raw_arboviroses_cases', engine)
    print(f"Foram lidos {len(df_raw)} registros brutos.")

    # --- NOVA ETAPA: REMOÇÃO DE DUPLICATAS ---
    print("Verificando e removendo registros duplicados...")
    # Definimos um conjunto de colunas que provavelmente identificam um caso único.
    # Você pode ajustar esta lista se encontrar uma chave primária melhor.
    colunas_chave = ['dt_notific', 'id_municip', 'nu_idade_n', 'cs_sexo', 'doenca_alvo']
    
    registros_antes = len(df_raw)
    # O método drop_duplicates remove linhas que têm valores idênticos nas colunas do 'subset'.
    # 'keep="first"' mantém a primeira ocorrência e remove as subsequentes.
    df_raw.drop_duplicates(subset=colunas_chave, keep='first', inplace=True)
    registros_depois = len(df_raw)
    
    print(f"{registros_antes - registros_depois} registros duplicados foram removidos.")
    print(f"Restaram {registros_depois} registros únicos para processamento.")

    # 3. LÓGICA DE LIMPEZA E TRANSFORMAÇÃO
    
    # Passo 3.1: Definir as colunas que realmente importam para o modelo
    symptom_columns = [
        'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea',
        'dor_costas', 'conjuntvit', 'artrite', 'artralgia', 'petequia_n',
        'leucopenia', 'dor_retro'
    ]
    target_column = 'doenca_alvo'
    
    relevant_columns = symptom_columns + [target_column]
    
    # Criamos um novo DataFrame APENAS com as colunas relevantes
    df = df_raw[relevant_columns].copy()
    print(f"Selecionadas {len(df.columns)} colunas relevantes para o modelo.")

    # Passo 3.2: Limpar a coluna alvo
    df.dropna(subset=[target_column], inplace=True)
    print(f"Registros após remover diagnósticos nulos: {len(df)}")

    # Passo 3.3: Binarizar os sintomas (Converter para 1s e 0s)
    print("Processando e binarizando colunas de sintomas...")
    for col in symptom_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: 1 if x == 1 else 0)

    # Passo 3.4: Remover registros sem nenhum sintoma registrado
    df = df[df[symptom_columns].sum(axis=1) > 0]
    print(f"Registros após remover casos sem sintomas: {len(df)}")

    # Passo 3.5: Codificar a variável alvo para números
    target_map = {'zika': 0, 'dengue': 1, 'chikungunya': 2}
    df['target_encoded'] = df[target_column].map(target_map)
    
    df.dropna(subset=['target_encoded'], inplace=True)
    df['target_encoded'] = df['target_encoded'].astype(int)
    print("Variável alvo ('doenca_alvo') codificada para formato numérico.")

    df_clean = df
    print(f"\nLimpeza de dados concluída. Total de {len(df_clean)} registros prontos para o treinamento.")

    # 4. Salvar os dados REALMENTE LIMPOS em uma nova tabela
    print("\nSalvando dados limpos na tabela 'cleaned_arboviroses_cases'...")
    # if_exists='replace' garante que a tabela antiga seja substituída pela nova
    df_clean.to_sql('cleaned_arboviroses_cases', engine, if_exists='replace', index=False)
    print("Dados limpos salvos com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante o processo de limpeza: {e}")