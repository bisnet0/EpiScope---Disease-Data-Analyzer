# backend/ingestion.py

import requests
import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- Funções de busca da API (do seu run.py) ---
def fetch_data(limit=100, offset=0):
    # ATENÇÃO: Verifique a documentação da API. A API que você usou parece não ter mais a chave 'parametros'.
    # A URL correta para Dengue, por exemplo, seria outra. Para Zika, os dados podem estar em 'results'.
    # Vou ajustar para o que parece ser o novo padrão.
    url = f'https://apidadosabertos.saude.gov.br/arboviroses/zikavirus?limit={limit}&offset={offset}'
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        dados_json = response.json()
        # MUDANÇA: A chave principal pode ser 'results' ou outra. Verifique a resposta da API.
        df = pd.DataFrame(dados_json) # Assumindo que a resposta já é uma lista de objetos
        return df
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API (offset: {offset}): {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Erro ao processar JSON (offset: {offset}): {e}")
        return None

def buscar_dados_paginados(num_paginas, limit_por_pagina=100):
    print(f"Iniciando busca de dados em até {num_paginas} páginas...")
    lista_de_dataframes = []
    
    for i in range(num_paginas):
        offset = i * limit_por_pagina
        print(f"Buscando página {i + 1}/{num_paginas} (offset: {offset})...")
        
        df_pagina = fetch_data(limit=limit_por_pagina, offset=offset)
        
        if df_pagina is not None and not df_pagina.empty:
            lista_de_dataframes.append(df_pagina)
        else:
            print(f"Página {i + 1} não retornou dados. A API pode ter chegado ao fim.")
            break
        time.sleep(1) # Boas práticas para não sobrecarregar a API

    if not lista_de_dataframes:
        print("Nenhum dado foi coletado.")
        return pd.DataFrame()

    df_completo = pd.concat(lista_de_dataframes, ignore_index=True)
    print(f"\nBusca finalizada. Total de {len(df_completo)} registros brutos coletados.")
    return df_completo

# --- LÓGICA PRINCIPAL DE INGESTÃO ---
if __name__ == "__main__":
    # NOVO: Conectando ao banco de dados com variáveis de ambiente para segurança
    # O Docker Compose vai garantir que a API consiga se conectar ao 'db' pelo nome do serviço.
    DB_USER = os.getenv("POSTGRES_USER", "bisnet0")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "RG4J8^%*TWjA*977Y40T81B2")
    DB_NAME = os.getenv("POSTGRES_DB", "episcope_db")
    DB_HOST = "db" # Usamos o nome do serviço do docker-compose
    DB_PORT = "5432"

    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Buscando os dados
    dados_brutos = buscar_dados_paginados(num_paginas=25, limit_por_pagina=20)

    if dados_brutos is not None and not dados_brutos.empty:
        try:
            print("\nConectando ao banco de dados para salvar os dados...")
            engine = create_engine(DB_URL)
            
            # ALTERAÇÃO: Salvando os dados brutos em uma tabela chamada 'raw_zika_cases'
            dados_brutos.to_sql('raw_zika_cases', engine, if_exists='replace', index=False)
            
            print(f"Dados salvos com sucesso na tabela 'raw_zika_cases' do banco '{DB_NAME}'!")
        except Exception as e:
            print(f"Falha ao salvar os dados no banco: {e}")