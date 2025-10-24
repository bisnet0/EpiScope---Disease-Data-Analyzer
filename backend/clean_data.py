# backend/clean_data.py (VERSÃO 2 - Anti-OOM Killer / Chunking)

import pandas as pd
from sqlalchemy import create_engine
import os

print("Iniciando processo de limpeza (v2 - Anti-OOM Killer / Chunking)...")

# 1. Conectar ao banco
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)
CHUNK_SIZE = 100000 # Processar 100.000 linhas por vez

try:
    # --- NOVO PASSO: Pré-calcular o Mediano Global ---
    print("Pré-calculando a mediana da idade global...")
    # Esta query é rápida, pois lê apenas uma coluna
    idade_series = pd.read_sql_query('SELECT "nu_idade_n" FROM raw_arboviroses_cases', engine)
    global_idade_median = pd.to_numeric(idade_series['nu_idade_n'], errors='coerce').median()
    print(f"Mediana da idade global calculada: {global_idade_median}")
    del idade_series # Libera memória

    # 2. Ler os dados brutos em CHUNKS
    query = 'SELECT * FROM raw_arboviroses_cases'
    reader = pd.read_sql(query, engine, chunksize=CHUNK_SIZE)
    
    total_rows_processed = 0
    is_first_chunk = True

    # 3. Lógica de Limpeza (aplicada a CADA CHUNK)
    for i, df_raw in enumerate(reader):
        print(f"Processando chunk {i+1} ({len(df_raw)} registros)...")
        
        # O drop_duplicates foi REMOVIDO. 
        # O script 'ingest_new_data.py V4' já garante que não há duplicatas na tabela raw.
        
        # 3.1: Definir colunas
        symptom_columns = [
            'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea',
            'dor_costas', 'conjuntvit', 'artrite', 'artralgia', 'petequia_n',
            'leucopenia', 'dor_retro'
        ]
        relevant_cols = symptom_columns + ['criterio', 'resul_ns1', 'cs_sexo', 'nu_idade_n', 'doenca_alvo']
        
        # Filtra apenas colunas que realmente existem no chunk
        cols_to_select = [col for col in relevant_cols if col in df_raw.columns]
        df = df_raw[cols_to_select].copy()

        # 3.2: Limpeza básica
        df.dropna(subset=['doenca_alvo'], inplace=True)
        if df.empty:
            print("  Chunk vazio após dropar nulos de 'doenca_alvo'. Pulando.")
            continue

        # 3.3: Binarizar os sintomas
        for col in symptom_columns:
            if col in df.columns: 
                df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: 1 if x == 1 else 0)

        # 3.4: Tratar demográficos (usando a mediana GLOBAL)
        df['sexo_encoded'] = df['cs_sexo'].map({'M': 0, 'F': 1}).fillna(-1)
        df['idade'] = pd.to_numeric(df['nu_idade_n'], errors='coerce')
        # Usamos a mediana global que pré-calculamos
        df['idade'] = df['idade'].fillna(global_idade_median) 

        # 3.5: Codificar features de diagnóstico
        df['ns1_encoded'] = pd.to_numeric(df.get('resul_ns1'), errors='coerce').map({1: 1, 2: 0, 3: -1, 4: -2}).fillna(-99)
        
        # Lógica de One-Hot-Encoding MANUAL (segura para chunks)
        df['criterio_num'] = pd.to_numeric(df.get('criterio'), errors='coerce').fillna(0).astype(int)
        df['criterio_0'] = (df['criterio_num'] == 0).astype(int)
        df['criterio_1'] = (df['criterio_num'] == 1).astype(int)
        df['criterio_2'] = (df['criterio_num'] == 2).astype(int)
        df['criterio_3'] = (df['criterio_num'] == 3).astype(int)
        
        # 3.6: Codificar a variável alvo
        target_map = {'zika': 0, 'dengue': 1, 'chikungunya': 2}
        target_column = 'doenca_alvo'
        df['target_encoded'] = df[target_column].map(target_map)
        df.dropna(subset=['target_encoded'], inplace=True)
        df['target_encoded'] = df['target_encoded'].astype(int)
        
        # 3.7: Montar o DataFrame limpo
        final_feature_columns = symptom_columns + ['sexo_encoded', 'idade', 'ns1_encoded', 'criterio_0', 'criterio_1', 'criterio_2', 'criterio_3']
        
        # Garante que todas as colunas de sintomas existam
        for col in final_feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        df_clean = df[final_feature_columns + [target_column, 'target_encoded']]
        total_rows_processed += len(df_clean)

        # 4. Salvar o chunk limpo
        if is_first_chunk:
            # O primeiro chunk apaga a tabela antiga (do run anterior)
            df_clean.to_sql('cleaned_arboviroses_cases', engine, if_exists='replace', index=False)
            print(f"  ...Primeiro chunk limpo salvo (tabela 'cleaned_arboviroses_cases' REINICIADA).")
            is_first_chunk = False
        else:
            # Os chunks seguintes fazem append
            df_clean.to_sql('cleaned_arboviroses_cases', engine, if_exists='append', index=False)
            print(f"  ...Chunk {i+1} limpo salvo (append).")

    print(f"\nLimpeza de dados (v2) concluída. Total de {total_rows_processed} registros prontos e salvos.")
    
    print("Calculando distribuição final das doenças na tabela limpa...")
    dist_final = pd.read_sql('SELECT doenca_alvo, COUNT(*) as count FROM cleaned_arboviroses_cases GROUP BY doenca_alvo', engine)
    print(dist_final.to_string(index=False))

except Exception as e:
    print(f"Ocorreu um erro durante o processo de limpeza: {e}")