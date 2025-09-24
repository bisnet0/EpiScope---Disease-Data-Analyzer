# ingestion.py (exemplo simplificado)
import requests
import pandas as pd
from sqlalchemy import create_engine

# 1. Capturar dados
API_URL = f'https://apidadosabertos.saude.gov.br/arboviroses/zikavirus?limit={limit}&offset={offset}'
response = requests.get(API_URL)
raw_data = response.json()

# 2. Limpar e estruturar com Pandas
df = pd.json_normalize(raw_data)
# ... aqui entra sua lógica de limpeza, renomeação de colunas, etc.
# Ex: df_clean = df[['sintoma1', 'sintoma2', 'diagnostico']].dropna()

# 3. Conectar e salvar no PostgreSQL
DB_URL = "postgresql://bisnet0:RG4J8^%*TWjA*977Y40T81B2@localhost:5432/episcope_db"
engine = create_engine(DB_URL)

# Supondo que df_clean é seu DataFrame final
# df_clean.to_sql('cases', engine, if_exists='replace', index=False)

print("Dados ingeridos com sucesso!")