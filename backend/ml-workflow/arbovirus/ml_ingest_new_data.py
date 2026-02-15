import pandas as pd
import os
import glob
import time
from sqlalchemy import create_engine, text
from io import StringIO

# ======================
# CONFIGURAÇÃO
# ======================

DOENCA_ALVO = "zika"  # "dengue" | "chikungunya" | "zika"
CHUNK_SIZE = 100_000 # Reduzi um pouco para garantir estabilidade na RAM

TABLE_FINAL = "raw_arboviroses_cases"

STAGING_TABLES = {
    "dengue": "temp_clean_dengue",
    "chikungunya": "temp_clean_chikungunya",
    "zika": "temp_clean_zika",
}

FILE_PREFIX = {
    "dengue": "DENG",
    "chikungunya": "CHIK",
    "zika": "ZIKA",
}

# ======================
# CONEXÃO
# ======================

DB_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@db:5432/"
    f"{os.getenv('POSTGRES_DB')}"
)
engine = create_engine(DB_URL)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
NEW_DATA_DIR = os.path.join(BACKEND_ROOT, "new_data")

STAGING_TABLE = STAGING_TABLES[DOENCA_ALVO]
FILE_PREFIX_DOENCA = FILE_PREFIX[DOENCA_ALVO]

# ======================
# FUNÇÕES
# ======================

def recreate_staging_table():
    print(f"\nRecriando staging: {STAGING_TABLE}")
    # Criamos apenas a estrutura, sem índices, constraints ou triggers
    sql = f"""
        DROP TABLE IF EXISTS {STAGING_TABLE};
        CREATE TABLE {STAGING_TABLE} AS 
        SELECT * FROM {TABLE_FINAL} WHERE 1=0;
    """
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(sql))

def copy_chunk_to_staging(df):
    buffer = StringIO()
    # Gravamos o CSV temporário com formato de data ISO (AAAA-MM-DD)
    df.to_csv(buffer, index=False, header=False, sep=';', date_format='%Y-%m-%d')
    buffer.seek(0)

    columns = ",".join([f'"{c}"' for c in df.columns])
    copy_sql = f"COPY {STAGING_TABLE} ({columns}) FROM STDIN WITH (FORMAT CSV, DELIMITER ';', NULL '')"

    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        cur.copy_expert(copy_sql, buffer)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro no COPY: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def process_csv(filepath):
    filename = os.path.basename(filepath)
    print(f"\nLendo {filename}...")
    
    total = 0
    try:
        reader = pd.read_csv(filepath, chunksize=CHUNK_SIZE, low_memory=False, encoding='utf-8')
    except UnicodeDecodeError:
        reader = pd.read_csv(filepath, chunksize=CHUNK_SIZE, low_memory=False, encoding='latin1')

    with engine.connect() as conn:
        res = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{TABLE_FINAL}'"))
        db_info = {row[0]: row[1] for row in res}
        db_cols = list(db_info.keys())

    for i, chunk in enumerate(reader):
        chunk.columns = chunk.columns.str.lower()
        chunk["doenca_alvo"] = DOENCA_ALVO

        # 1. Tratamento de Datas (O Coração do Ajuste)
        date_cols = [c for c, t in db_info.items() if 'date' in t.lower()]
        for col in date_cols:
            if col in chunk.columns:
                # Transforma lixo em NaT (Not a Time), que o to_csv vira NULL
                chunk[col] = pd.to_datetime(chunk[col], errors='coerce').dt.date

        # 2. Garante todas as colunas do banco
        for col in db_cols:
            if col not in chunk.columns:
                chunk[col] = None
        
        # 3. Reordena e limpa fragmentação
        chunk = chunk[db_cols].copy()

        copy_chunk_to_staging(chunk)
        total += len(chunk)
        print(f"  Chunk {i + 1} - {total} linhas processadas")

    return total

def merge_staging_into_final():
    print(f"\nFazendo merge {STAGING_TABLE} → {TABLE_FINAL}")
    # Use o nome exato da sua constraint de unicidade aqui
    sql = f"""
        INSERT INTO {TABLE_FINAL}
        SELECT * FROM {STAGING_TABLE}
        ON CONFLICT (dt_notific, id_municip, nu_idade_n, cs_sexo, dt_sin_pri, doenca_alvo) 
        DO NOTHING;
    """
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(sql))

def drop_staging():
    print(f"Limpando staging {STAGING_TABLE}")
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"DROP TABLE IF EXISTS {STAGING_TABLE}"))

def main():
    start = time.time()
    print(f"=== INGESTÃO DATA-SENSITIVE: {DOENCA_ALVO.upper()} ===")
    recreate_staging_table()
    files = sorted(glob.glob(os.path.join(NEW_DATA_DIR, f"{FILE_PREFIX_DOENCA}*.csv")))
    
    if not files:
        print("Nenhum arquivo encontrado.")
        return

    total_linhas = 0
    for f in files:
        total_linhas += process_csv(f)

    merge_staging_into_final()
    drop_staging()
    print(f"\n--- CONCLUÍDO EM {time.time() - start:.2f}s ---")

if __name__ == "__main__":
    main()