import os
from typing import Any
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI

def create_medical_agent() -> Any:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_name = os.getenv("POSTGRES_DB", "episcope")

    DB_URL = f"postgresql://{user}:{password}@db:5432/{db_name}"
    db = SQLDatabase.from_uri(DB_URL)
    
    # Padronizado com o resto do seu projeto!
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY") or "",
        temperature=0.0
    )
    
    sql_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

    return sql_chain