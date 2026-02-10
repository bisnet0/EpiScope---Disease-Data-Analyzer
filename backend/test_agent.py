# test_agent.py
import os
from dotenv import load_dotenv
load_dotenv() # Carrega sua API Key do .env

from langchain_core.messages import HumanMessage
from backend.agents.graph import app_graph

def chat_loop():
    print("👨‍⚕️ Dr. EpiScope (Terminal Mode) - Digite 'sair' para encerrar.")
    print("-------------------------------------------------------------")
    
    # Estado inicial vazio
    chat_history = []
    
    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["sair", "exit"]: break
        
        # Adiciona mensagem do usuário
        chat_history.append(HumanMessage(content=user_input))
        
        # Invoca o Agente
        print("🤖 Pensando...", end="\r")
        for event in app_graph.stream({"messages": chat_history}):
            for key, value in event.items():
                # Apenas debug para ver os nós rodando
                # print(f"  -> Atuando em: {key}") 
                pass
                
        # Pega a resposta final
        final_state = app_graph.invoke({"messages": chat_history})
        ai_msg = final_state["messages"][-1].content
        
        print(f"Dr. EpiScope: {ai_msg}\n")
        
        # Atualiza histórico (importante para ele lembrar que já perguntou a idade)
        chat_history = final_state["messages"]

if __name__ == "__main__":
    chat_loop()