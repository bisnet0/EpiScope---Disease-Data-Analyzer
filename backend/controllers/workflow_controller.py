from flask import request, jsonify
from backend.agents.hospital_workflow import app as hospital_workflow_app


def run_hospital_workflow():
    """
    Endpoint para disparar o fluxo de auditoria e decisão manualmente
    ou via integração interna.
    """
    try:
        data = request.get_json()
        diagnosis = data.get("diagnosis")

        if not diagnosis:
            return jsonify({"error": "O campo 'diagnosis' é obrigatório."}), 400

        result = hospital_workflow_app.invoke({"diagnosis": diagnosis})

        return jsonify(
            {
                "message": "Fluxo de decisão EpiScope finalizado com sucesso",
                "data": result,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar workflow: {str(e)}"}), 500
