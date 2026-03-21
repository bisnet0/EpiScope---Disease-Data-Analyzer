from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import ChatOpenAI
import os


def create_medical_agent():
    DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    db = SQLDatabase.from_uri(DB_URL)
    llm = ChatOpenAI(temperature=0)
    sql_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

    return sql_chain
