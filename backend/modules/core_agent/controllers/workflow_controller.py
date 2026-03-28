from flask import request, jsonify

# 👇 Mantido o import do seu workflow (ajustaremos isso quando fatiarmos a pasta agents)
from backend.agents.hospital_workflow import app as hospital_workflow_app

def run_hospital_workflow_internal(data):
    """
    Função AUXILIAR para ser chamada por outros controllers (Glaucoma/Xray)
    sem passar pela rota HTTP.
    """
    try:
        diagnosis = data.get("diagnosis")
        if not diagnosis:
            print("⚠️ [WORKFLOW]: Diagnosis vazio, pulando auditoria.")
            return None
        
        # Executa o grafo do LangGraph
        result = hospital_workflow_app.invoke({"diagnosis": diagnosis})
        return result
    except Exception as e:
        print(f"❌ [WORKFLOW ERROR]: {str(e)}")
        return None

def run_hospital_workflow():
    """
    Endpoint (POST) para disparar o fluxo via API.
    """
    try:
        data = request.get_json()
        result = run_hospital_workflow_internal(data) # Reutiliza a lógica acima

        if result is None:
            return jsonify({"error": "Erro ao processar workflow interno"}), 500

        return jsonify({
            "message": "Fluxo de decisão EpiScope finalizado com sucesso",
            "data": result,
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar workflow: {str(e)}"}), 500