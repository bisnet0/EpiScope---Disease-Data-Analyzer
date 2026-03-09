import pandas as pd
from sqlalchemy import create_engine, text
import os
import time
import gc
from io import StringIO

print("Iniciando Limpeza via COPY (v7 - Engine de Ingestão)...")
start_time = time.time()

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

CHUNK_SIZE = 100000 
STAGING_CLEAN = "temp_staging_clean_all"
FINAL_TABLE = "cleaned_arboviroses_cases"

def copy_to_db(df, table_name):
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, sep=';')
    buffer.seek(0)
    
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.copy_from(buffer, table_name, sep=';', null='')
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro no COPY: {e}")
    finally:
        conn.close()

try:
    # 1. Mediana
    with engine.connect() as conn:
        print("Calculando mediana no banco...")
        res = conn.execute(text('SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY nu_idade_n::numeric) FROM raw_arboviroses_cases'))
        global_idade_median = res.scalar() or 4032.0

    # 2. Preparar Staging
    symptom_columns = [
        "febre", "mialgia", "cefaleia", "exantema", "vomito", 
        "nausea", "dor_costas", "conjuntvit", "artrite", 
        "artralgia", "petequia_n", "leucopenia", "dor_retro"
    ]
    
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {STAGING_CLEAN}"))
        # Criamos a tabela manualmente para garantir os tipos
        cols_sql = ", ".join([f"{col} INT" for col in symptom_columns])
        conn.execute(text(f"""
            CREATE TABLE {STAGING_CLEAN} (
                {cols_sql},
                sexo_encoded INT,
                idade FLOAT,
                doenca_alvo TEXT,
                target_encoded INT
            )
        """))
        conn.commit()

    # 3. Loop de Processamento
    query = f'SELECT {", ".join(symptom_columns + ["cs_sexo", "nu_idade_n", "doenca_alvo"])} FROM raw_arboviroses_cases'
    
    # Usando o modo stream do SQLAlchemy para não estourar a RAM
    conn = engine.connect().execution_options(stream_results=True)
    
    print("Iniciando limpeza e stream para staging...")
    for i, df in enumerate(pd.read_sql(query, conn, chunksize=CHUNK_SIZE)):
        # Desfragmenta e limpa
        df = df.copy()

        # Limpeza de sintomas
        for col in symptom_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        # Trata Sexo e Idade
        df["sexo_encoded"] = df["cs_sexo"].map({"M": 0, "F": 1}).fillna(-1).astype(int)
        df["idade"] = pd.to_numeric(df["nu_idade_n"], errors="coerce").fillna(global_idade_median).astype(float)

        # Target
        target_map = {"zika": 0, "dengue": 1, "chikungunya": 2}
        df["target_encoded"] = df["doenca_alvo"].map(target_map)
        
        # Filtra e garante TIPAGEM correta para o COPY não bugar com .0
        df_to_save = df[symptom_columns + ["sexo_encoded", "idade", "doenca_alvo", "target_encoded"]].dropna(subset=["target_encoded"])
        
        # Converte explicitamente as colunas inteiras para tirar o .0
        cols_to_fix = symptom_columns + ["sexo_encoded", "target_encoded"]
        df_to_save[cols_to_fix] = df_to_save[cols_to_fix].astype(int)
        
        copy_to_db(df_to_save, STAGING_CLEAN)
        
        if (i + 1) % 5 == 0:
            print(f"  > {(i + 1) * CHUNK_SIZE} processados...")
            gc.collect()

    conn.close()

    # 4. Balanceamento (Undersampling)
    print("\nBalanceando classes...")
    with engine.connect() as conn:
        counts = conn.execute(text(f"SELECT doenca_alvo, COUNT(*) FROM {STAGING_CLEAN} GROUP BY doenca_alvo")).all()
        min_count = int(min([row[1] for row in counts]))
        print(f"Contagens: {counts} | Alvo: {min_count}")

        conn.execute(text(f"DROP TABLE IF EXISTS {FINAL_TABLE}"))
        conn.execute(text(f"""
            CREATE TABLE {FINAL_TABLE} AS (
                (SELECT * FROM {STAGING_CLEAN} WHERE doenca_alvo = 'dengue' ORDER BY RANDOM() LIMIT {min_count})
                UNION ALL
                (SELECT * FROM {STAGING_CLEAN} WHERE doenca_alvo = 'zika' ORDER BY RANDOM() LIMIT {min_count})
                UNION ALL
                (SELECT * FROM {STAGING_CLEAN} WHERE doenca_alvo = 'chikungunya' ORDER BY RANDOM() LIMIT {min_count})
            )
        """))
        conn.execute(text(f"DROP TABLE IF EXISTS {STAGING_CLEAN}"))
        conn.commit()

    print(f"\n✅ CONCLUÍDO EM {time.time() - start_time:.2f}s")

except Exception as e:
    print(f"Erro: {e}")