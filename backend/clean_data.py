# backend/clean_data.py

import pandas as pd
from sqlalchemy import create_engine
import os

print("Iniciando processo de limpeza e transformação de dados...")

# 1. Conectar ao banco de dados (usando as mesmas variáveis de ambiente)
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
    print(f"Foram lidos {len(df_raw)} registros.")

    # 3. APLICAR SUA LÓGICA DE LIMPEZA AQUI!
    # Exemplo:
    # df_clean = df_raw.dropna(subset=['coluna_importante_1', 'coluna_importante_2'])
    # df_clean['idade'] = pd.to_numeric(df_clean['idade'], errors='coerce')
    # ... etc ...
    
    # Por enquanto, vamos apenas usar o mesmo dataframe como exemplo
    df_clean = df_raw.copy() 
    print("Limpeza de dados concluída (lógica de exemplo).")

    # 4. Salvar os dados limpos em uma nova tabela
    print("Salvando dados limpos na tabela 'cleaned_arboviroses_cases'...")
    df_clean.to_sql('cleaned_arboviroses_cases', engine, if_exists='replace', index=False)
    print("Dados limpos salvos com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante o processo de limpeza: {e}")