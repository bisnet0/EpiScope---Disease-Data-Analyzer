# backend/agents/state.py
from typing import TypedDict, Annotated, List, Union
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # O histórico da conversa (User + AI)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Contexto Médico Extraído (ex: {"febre": True, "age": 30})
    medical_context: dict
    
    # Qual o próximo passo? (ex: "ask_user", "call_tool", "finish")
    next_step: str
    
    # Resultado bruto das ferramentas (probabilidades do XGBoost ou CNN)
    tool_output: dict
    
    # Quantas vezes ele já perguntou ao usuário (para evitar loops infinitos)
    retry_count: int