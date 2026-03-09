import os
import traceback
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURAÇÃO GLOBAL ---
import google.generativeai as genai
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key if api_key else ""
if api_key:
    genai.configure(api_key=api_key)

from langchain_core.messages import HumanMessage
from backend.agents.graph import app_graph
from backend.app import app

def chat_loop():
    print("💀 Dr. EpiScope (DEBUG BRUTAL) - Digite 'sair' para encerrar.")
    print("-------------------------------------------------------------")
    
    chat_history = []
    
    with app.app_context():
        while True:
            user_input = input("\nVocê: ")
            if user_input.lower() in ["sair", "exit"]: break
            
            chat_history.append(HumanMessage(content=user_input))
            print("🤖 Pensando (Rastreando chamadas de API)...", end="\r")
            
            try:
                # Recursion limit alto para garantir que não pare no meio
                final_state = app_graph.invoke(
                    {"messages": chat_history}, 
                    config={"recursion_limit": 15}
                )
                
                ai_msg = final_state["messages"][-1].content
                print(f"Dr. EpiScope: {ai_msg}")
                chat_history = final_state["messages"]
                
            except Exception:
                print("\n\n🔥 ERRO CRÍTICO CAPTURADO 🔥")
                print("------------------------------------------------")
                # Imprime o erro exato que o Google devolveu
                traceback.print_exc()
                print("------------------------------------------------")
                print("DICA: Procure por '429' ou 'RESOURCE_EXHAUSTED' no texto acima.")

if __name__ == "__main__":
    chat_loop()