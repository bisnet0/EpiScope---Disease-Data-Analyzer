# backend/diagnose_data.py
import pandas as pd
from sqlalchemy import create_engine
import os

# Configura o pandas para mostrar todas as linhas ao imprimir
pd.set_option('display.max_rows', None)

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

print("Lendo dados brutos para diagnóstico...")
df_raw = pd.read_sql('SELECT * FROM raw_arboviroses_cases', engine)
df_raw.drop_duplicates(subset=['dt_notific', 'id_municip', 'nu_idade_n', 'cs_sexo', 'doenca_alvo'], keep='first', inplace=True)


print("\n--- Contagem de valores NÃO NULOS por coluna (para cada doença) ---")
# Agrupa por doença e conta quantos valores não nulos existem em cada coluna
diagnostico = df_raw.groupby('doenca_alvo').count().transpose()

# Mostra a contagem para cada doença e ordena pelas colunas mais preenchidas
print(diagnostico.sort_values(by='zika', ascending=False).head(40))
print("-" * 50)
print(diagnostico.sort_values(by='chikungunya', ascending=False).head(40))