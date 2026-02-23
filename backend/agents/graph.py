import os
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage

from backend.agents.state import AgentState
from backend.agents.tools import MEDICAL_TOOLS

# 1. Configuração do LLM (O Cérebro)
# O Gemini precisa saber que ferramentas ele tem à disposição.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2, # Baixa temperatura para ser mais preciso/médico
    max_retries=2
).bind_tools(MEDICAL_TOOLS)

# 2. O Prompt do Sistema (A Personalidade "Parruda")
SYSTEM_PROMPT = """
Você é o Dr. EpiScope, um Supervisor Médico de IA avançado.
Sua missão é triar pacientes e coordenar diagnósticos complexos.

REGRAS DE CONDUTA:
1. ANAMNESE (Texto):
   - Se o usuário relatar sintomas, verifique se você tem: SINTOMAS, IDADE e SEXO.
   - Se faltar algo, NÃO chame a ferramenta. PERGUNTE ao usuário (ex: "Para precisão, qual sua idade?").
   - Apenas quando tiver tudo, chame a ferramenta 'arbovirus_specialist'.

2. VISÃO (Imagem):
   - Se receber dados de imagem, chame imediatamente 'glaucoma_specialist'.

3. LABORATÓRIO (Admin):
   - Se o usuário falar sobre "evoluir", "treinar" ou "otimizar", chame 'lab_manager'.

4. POSTURA:
   - Seja direto, profissional e empático.
   - NUNCA invente diagnósticos médicos. Use APENAS o retorno das suas ferramentas.
   - Se a ferramenta der erro, peça desculpas e peça para tentar novamente.
"""

# 3. Nó Supervisor (O Roteador)
def supervisor_node(state: AgentState):
    messages = state['messages']
    
    # Se for a primeira mensagem, injeta a personalidade
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    # O LLM "pensa" e decide o próximo passo (Texto ou Chamada de Ferramenta)
    response = llm.invoke(messages)
    return {"messages": [response]}

# 4. Lógica Condicional (A Inteligência do Grafo)
def should_continue(state: AgentState) -> Literal["tools", "final"]:
    last_message = state['messages'][-1]
    
    # Se o LLM decidiu chamar uma ferramenta (tool_calls), vamos para o nó de ferramentas
    if last_message.tool_calls:
        return "tools"
    
    # Se ele respondeu texto normal (ex: uma pergunta ao usuário), paramos por aqui e devolvemos ao front
    return "final"

# 5. Construção do Grafo (Wiring)
workflow = StateGraph(AgentState)

# Adiciona os Nós
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("tools", ToolNode(MEDICAL_TOOLS)) # Nó pré-construído do LangGraph que executa as funções

# Define o Fluxo
workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    should_continue,
    {
        "tools": "tools",  # Se precisar de ferramenta, vai para 'tools'
        "final": END       # Se for texto, encerra o ciclo (aguarda input do user)
    }
)

# Se a ferramenta rodar, volta para o supervisor interpretar o resultado (Loop de Feedback)
workflow.add_edge("tools", "supervisor")

# Compila o Grafo
app_graph = workflow.compile()