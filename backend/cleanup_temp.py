# backend/cleanup_temp.py
import os
from sqlalchemy import create_engine, text

print("Iniciando script de limpeza de tabelas temporárias...")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

TEMP_TABLE_DENGUE = 'temp_clean_dengue'
TEMP_TABLE_ZIKA = 'temp_clean_zika'
TEMP_TABLE_CHIK = 'temp_clean_chikungunya'

try:
    with engine.connect() as conn:
        with conn.begin(): # Usar uma transação
            print(f"Tentando dropar {TEMP_TABLE_DENGUE}...")
            # A CORREÇÃO: envelopar o SQL com a função text()
            conn.execute(text(f'DROP TABLE IF EXISTS {TEMP_TABLE_DENGUE}'))
            
            print(f"Tentando dropar {TEMP_TABLE_ZIKA}...")
            conn.execute(text(f'DROP TABLE IF EXISTS {TEMP_TABLE_ZIKA}'))
            
            print(f"Tentando dropar {TEMP_TABLE_CHIK}...")
            conn.execute(text(f'DROP TABLE IF EXISTS {TEMP_TABLE_CHIK}'))
    
    print("Tabelas temporárias limpas com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro ao limpar as tabelas: {e}")