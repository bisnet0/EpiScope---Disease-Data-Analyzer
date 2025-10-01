# backend/ingestion.py

import requests
import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_data(url, limit=20, offset=0):
    """Função genérica para buscar dados de uma URL da API."""
    paginated_url = f'{url}?limit={limit}&offset={offset}'
    try:
        response = requests.get(paginated_url, timeout=30)
        response.raise_for_status()
        dados_json = response.json()
        if 'parametros' in dados_json and dados_json['parametros']:
            return pd.DataFrame(dados_json['parametros'])
        else:
            print(f"Resposta vazia ou sem chave 'parametros' (URL: {paginated_url})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição (offset {offset}): {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Erro ao processar JSON (offset {offset}): {e}")
        return None


def buscar_dados_paginados(disease_name, disease_url, limit_por_pagina=20, num_paginas=10):
    """Busca dados paginados para uma doença específica em até num_paginas."""
    print(f"\n--- Iniciando busca para: {disease_name.upper()} ---")
    lista_de_dataframes = []

    for pagina in range(num_paginas):
        offset = pagina * limit_por_pagina 
        print(f"Buscando página {pagina + 1}/{num_paginas} (offset: {offset})...")

        df_pagina = fetch_data(disease_url, limit=limit_por_pagina, offset=offset)

        if df_pagina is not None and not df_pagina.empty:
            lista_de_dataframes.append(df_pagina)
        else:
            print(f"Fim dos dados para {disease_name}. Última página: {pagina + 1}")
            break

        time.sleep(1)

    if not lista_de_dataframes:
        print(f"Nenhum dado coletado para {disease_name}.")
        return pd.DataFrame()

    df_completo = pd.concat(lista_de_dataframes, ignore_index=True)
    print(f"Busca para {disease_name} finalizada. Total de {len(df_completo)} registros coletados.")
    return df_completo


if __name__ == "__main__":
    # Endpoints das doenças
    doencas_endpoints = {
        'zika': 'https://apidadosabertos.saude.gov.br/arboviroses/zikavirus',
        'dengue': 'https://apidadosabertos.saude.gov.br/arboviroses/dengue',
        'chikungunya': 'https://apidadosabertos.saude.gov.br/arboviroses/chikungunya'
    }

    todos_os_dados = []

    for nome, url in doencas_endpoints.items():
        dados_doenca = buscar_dados_paginados(nome, url, limit_por_pagina=20, num_paginas=50)
        if not dados_doenca.empty:
            dados_doenca['doenca_alvo'] = nome
            todos_os_dados.append(dados_doenca)

    if not todos_os_dados:
        print("Nenhum dado foi coletado de nenhuma fonte. Encerrando.")
    else:
        df_final_bruto = pd.concat(todos_os_dados, ignore_index=True)
        print(f"\nTotal de registros combinados: {len(df_final_bruto)}")
        print("Distribuição por doença:")
        print(df_final_bruto['doenca_alvo'].value_counts())

        DB_USER = os.getenv("POSTGRES_USER")
        DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        DB_NAME = os.getenv("POSTGRES_DB")
        DB_HOST = "db"
        DB_PORT = "5432"
        DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        try:
            engine = create_engine(DB_URL)
            print("\nSalvando dados no PostgreSQL...")
            df_final_bruto.to_sql('raw_arboviroses_cases', engine, if_exists='replace', index=False)
            print("Dados salvos com sucesso em 'raw_arboviroses_cases'!")
        except Exception as e:
            print(f"Falha ao salvar no banco: {e}")
