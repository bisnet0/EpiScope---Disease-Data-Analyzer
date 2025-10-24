# backend/ingest_new_data.py (VERSÃO 4 - Correção OOM Killer / Salva por Chunk)

import pandas as pd
from sqlalchemy import create_engine, inspect
import os
import glob
import time
import ijson
import itertools

print("Iniciando script de ingestão de novos dados (v4 - Correção OOM Killer)...")

# --- Configuração ---
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

NEW_DATA_DIR = "new_data"
COMPOSITE_KEY_COLS = ['dt_notific', 'id_municip', 'nu_idade_n', 'cs_sexo', 'dt_sin_pri', 'doenca_alvo']
CHUNK_SIZE = 50000 

# --- Funções ---
def get_existing_keys(engine):
    print("Buscando chaves existentes no banco de dados para evitar duplicatas...")
    query = f"SELECT {', '.join(COMPOSITE_KEY_COLS)} FROM raw_arboviroses_cases"
    
    try:
        existing_data_iter = pd.read_sql(query, engine, chunksize=CHUNK_SIZE)
        existing_keys = set()
        
        for chunk in existing_data_iter:
            keys_in_chunk = [tuple(x) for x in chunk.to_numpy()]
            existing_keys.update(keys_in_chunk)
            
        print(f"Encontradas {len(existing_keys)} chaves únicas existentes.")
        return existing_keys
    except Exception as e:
        print(f"Tabela 'raw_arboviroses_cases' ainda não existe? {e}. Iniciando com zero chaves.")
        return set()

# --- MUDANÇA AQUI: A função agora salva no DB e retorna contagens ---
def process_file(filepath, existing_keys, engine, db_columns):
    """
    Processa um único arquivo (JSON ou CSV), limpa, remove duplicatas E SALVA NO BANCO chunk-por-chunk.
    """
    filename = os.path.basename(filepath)
    print(f"\nProcessando arquivo: {filename}...")
    
    if 'chikungunya' in filename.lower():
        doenca_alvo = 'chikungunya'
    elif 'dengue' in filename.lower():
        doenca_alvo = 'dengue'
    elif 'zika' in filename.lower():
        doenca_alvo = 'zika'
    else:
        print(f"AVISO: Não foi possível determinar a doença para {filename}. Pulando arquivo.")
        return 0, 0 # Retorna 0 processados, 0 inseridos

    # 2. LER O ARQUIVO
    reader = None
    if filepath.endswith('.json'):
        try:
            print(f"  Abrindo {filename} com streaming parser (ijson)...")
            f = open(filepath, 'rb')
            objects = ijson.items(f, 'item')
            reader = iter(lambda: list(itertools.islice(objects, CHUNK_SIZE)), [])
        except Exception as e:
            print(f"  ERRO: Falha ao abrir {filename} com ijson. Erro: {e}")
            if 'f' in locals(): f.close()
            return 0, 0
            
    elif filepath.endswith('.csv'):
        reader = pd.read_csv(filepath, chunksize=CHUNK_SIZE, low_memory=False)
    else:
        print(f"Formato de arquivo não suportado: {filename}. Pulando.")
        return 0, 0

    total_rows_in_file = 0
    total_rows_inserted = 0

    try:
        for i, data_chunk in enumerate(reader):
            if not data_chunk: 
                break

            if filepath.endswith('.json'):
                chunk = pd.DataFrame.from_records(data_chunk)
            else:
                chunk = data_chunk 

            print(f"  ...processando chunk {i+1} ({len(chunk)} registros)")

            chunk.columns = chunk.columns.str.lower()
            chunk['doenca_alvo'] = doenca_alvo
            
            for col in COMPOSITE_KEY_COLS:
                if col not in chunk.columns:
                    chunk[col] = None 
            
            total_rows_in_file += len(chunk)

            chunk_keys = chunk[COMPOSITE_KEY_COLS].astype(str).values.tolist()
            chunk['composite_key'] = [tuple(key) for key in chunk_keys]

            new_rows_chunk = chunk[~chunk['composite_key'].isin(existing_keys)]
            existing_keys.update(new_rows_chunk['composite_key'])
            
            # --- MUDANÇA AQUI: Salva o chunk no DB imediatamente ---
            if not new_rows_chunk.empty:
                rows_to_insert_count = len(new_rows_chunk)
                total_rows_inserted += rows_to_insert_count
                
                # Filtra o chunk para ter APENAS as colunas que existem no banco
                new_rows_chunk_filtered = new_rows_chunk[new_rows_chunk.columns.intersection(db_columns)]
                
                try:
                    new_rows_chunk_filtered.to_sql('raw_arboviroses_cases', engine, if_exists='append', index=False)
                    print(f"  ...SALVO: {rows_to_insert_count} novos registros inseridos no banco.")
                except Exception as e:
                    print(f"  ...ERRO AO SALVAR CHUNK: {e}")
            # --- FIM DA MUDANÇA ---

    finally:
        if filepath.endswith('.json') and 'f' in locals():
            f.close()
            print(f"  Arquivo {filename} fechado.")

    print(f"Arquivo {filename} processado. Total de {total_rows_in_file} linhas. {total_rows_inserted} linhas novas inseridas.")
    return total_rows_in_file, total_rows_inserted


# --- Execução Principal (Refatorada) ---
def main():
    start_time = time.time()
    
    # 1. Pega as chaves que já estão no banco
    existing_keys = get_existing_keys(engine)
    
    # 2. Pega as colunas do DB UMA VEZ
    try:
        inspector = inspect(engine)
        db_columns = [col['name'] for col in inspector.get_columns('raw_arboviroses_cases')]
        if not db_columns:
             print("ERRO: Tabela 'raw_arboviroses_cases' parece não ter colunas.")
             return
    except Exception as e:
        print(f"ERRO: Não foi possível inspecionar colunas do banco. A tabela existe? Erro: {e}")
        return

    # 3. Encontra todos os arquivos de dados na pasta
    files_to_process = glob.glob(os.path.join(NEW_DATA_DIR, "*.*"))
    if not files_to_process:
        print(f"Nenhum arquivo encontrado em '{NEW_DATA_DIR}'. Encerrando.")
        return

    print(f"Encontrados {len(files_to_process)} arquivos para processar.")
    
    grand_total_processed = 0
    grand_total_inserted = 0

    # 4. Processa cada arquivo (que agora salva por conta própria)
    for f in files_to_process:
        processed, inserted = process_file(f, existing_keys, engine, db_columns)
        grand_total_processed += processed
        grand_total_inserted += inserted

    end_time = time.time()
    print("\n--- Processamento Concluído ---")
    print(f"Total de linhas lidas: {grand_total_processed}")
    print(f"Total de NOVAS linhas inseridas no banco: {grand_total_inserted}")
    print(f"Ingestão concluída em {end_time - start_time:.2f} segundos.")


if __name__ == "__main__":
    main()