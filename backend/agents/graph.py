import os
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage

from backend.agents.state import AgentState
from backend.agents.tools import MEDICAL_TOOLS


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
    max_retries=2,
).bind_tools(MEDICAL_TOOLS)


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


def supervisor_node(state: AgentState):
    messages = state["messages"]

    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "final"]:
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return "final"


workflow = StateGraph(AgentState)


workflow.add_node("supervisor", supervisor_node)
workflow.add_node("tools", ToolNode(MEDICAL_TOOLS))


workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor", should_continue, {"tools": "tools", "final": END}
)


workflow.add_edge("tools", "supervisor")


app_graph = workflow.compile()
