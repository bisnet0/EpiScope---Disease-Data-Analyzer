from langchain.tools import tool

# O serviço de RAG pode continuar no local antigo até refatorarmos a pasta services,
# ou já pode ir para modules/core_agent/services/rag_service.py futuramente.
from backend.modules.core_agent.services.rag_service import search_knowledge_base

@tool("rag_clinical_tool")
def rag_clinical_tool(query: str):
    """
    Busca na base de conhecimento (PDFs médicos, protocolos do Ministério da Saúde, artigos científicos).
    USE ESTA FERRAMENTA SEMPRE que o paciente pedir explicações aprofundadas sobre Dengue, Zika, Chikungunya ou Glaucoma,
    ou quando precisar recomendar procedimentos, laudos estruturados e diretrizes clínicas oficiais.
    """
    print(f"\n[AGENTE] 📚 Consultando a biblioteca médica para: '{query}'...")

    resultado_busca = search_knowledge_base(query=query, k=4)

    return f"""
    RESULTADOS DA BUSCA NA LITERATURA CLÍNICA:
    {resultado_busca}
    
    INSTRUÇÃO AO AGENTE: Use os trechos acima para embasar sua resposta. Cite a fonte de forma natural se aplicável.
    """