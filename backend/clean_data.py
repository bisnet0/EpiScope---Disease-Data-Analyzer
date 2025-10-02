# backend/clean_data.py

import pandas as pd
from sqlalchemy import create_engine
import os

print("Iniciando processo de limpeza e transformação de dados (Estratégia Híbrida)...")

# 1. Conectar ao banco de dados
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DB_URL)

try:
    # 2. Ler os dados brutos e remover duplicatas
    df_raw = pd.read_sql('SELECT * FROM raw_arboviroses_cases', engine)
    print(f"Foram lidos {len(df_raw)} registros brutos.")
    colunas_chave = ['dt_notific', 'id_municip', 'nu_idade_n', 'cs_sexo', 'doenca_alvo']
    df_raw.drop_duplicates(subset=colunas_chave, keep='first', inplace=True)
    print(f"Restaram {len(df_raw)} registros únicos.")

    # 3. LÓGICA DE LIMPEZA E TRANSFORMAÇÃO
    
    # Passo 3.1: Definir as colunas que importam (agora incluindo as novas!)
    symptom_columns = [
        'febre', 'mialgia', 'cefaleia', 'exantema', 'vomito', 'nausea',
        'dor_costas', 'conjuntvit', 'artrite', 'artralgia', 'petequia_n',
        'leucopenia', 'dor_retro'
    ]
    diagnostic_columns = ['criterio', 'resul_ns1'] # <-- NOVAS FEATURES
    demographic_columns = ['cs_sexo', 'nu_idade_n']
    target_column = 'doenca_alvo'
    
    relevant_columns = symptom_columns + diagnostic_columns + demographic_columns + [target_column]
    df = df_raw[relevant_columns].copy()

    # Passo 3.2: Limpeza básica
    df.dropna(subset=[target_column], inplace=True)

    # Passo 3.3: Binarizar os sintomas
    for col in symptom_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: 1 if x == 1 else 0)

    # Passo 3.4: Limpar e tratar colunas demográficas
    df['sexo_encoded'] = df['cs_sexo'].map({'M': 0, 'F': 1}).fillna(-1) # M=0, F=1, Outro=-1
    df['idade'] = pd.to_numeric(df['nu_idade_n'], errors='coerce')
    df['idade'].fillna(df['idade'].median(), inplace=True)

    # Passo 3.5: Limpar e codificar as NOVAS features de diagnóstico
    # 'resul_ns1': 1=Reagente, 2=Não Reagente, 3=Inconclusivo, 4=Não realizado
    # Vamos mapear para valores numéricos simples
    df['ns1_encoded'] = pd.to_numeric(df['resul_ns1'], errors='coerce').map({1: 1, 2: 0, 3: -1, 4: -2}).fillna(-99) # Reagente=1, N_Reagente=0, Outros/Nulo=-99

    # 'criterio': Usaremos One-Hot Encoding para transformar categorias em colunas
    df['criterio'] = pd.to_numeric(df['criterio'], errors='coerce').fillna(0).astype(int) # Preenche nulos com 0
    df = pd.get_dummies(df, columns=['criterio'], prefix='criterio')

    # Passo 3.6: Codificar a variável alvo
    target_map = {'zika': 0, 'dengue': 1, 'chikungunya': 2}
    df['target_encoded'] = df[target_column].map(target_map)
    df.dropna(subset=['target_encoded'], inplace=True)
    df['target_encoded'] = df['target_encoded'].astype(int)
    
    # Passo 3.7: Definir colunas finais e montar o DataFrame limpo
    # Coletamos as novas colunas criadas pelo get_dummies
    criterio_cols = [col for col in df.columns if col.startswith('criterio_')]
    
    final_feature_columns = symptom_columns + ['sexo_encoded', 'idade', 'ns1_encoded'] + criterio_cols
    df_clean = df[final_feature_columns + [target_column, 'target_encoded']]
    
    print(f"\nLimpeza de dados (Estratégia Híbrida) concluída. Total de {len(df_clean)} registros prontos.")
    print("Distribuição final das doenças:")
    print(df_clean[target_column].value_counts()) # <-- VAMOS VER SE AGORA TEMOS AS 3 DOENÇAS

    # 4. Salvar os dados limpos
    df_clean.to_sql('cleaned_arboviroses_cases', engine, if_exists='replace', index=False)
    print("Dados limpos salvos com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante o processo de limpeza: {e}")