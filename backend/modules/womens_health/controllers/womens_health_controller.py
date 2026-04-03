from flask import request, jsonify
from backend.modules.womens_health.services.audio_analysis_service import (
    process_consultation_audio,
)


def analyze_womens_audio():
    """
    Recebe um arquivo de áudio de uma consulta (ex: acompanhamento pós-parto)
    e analisa sinais de hesitação, tom de voz e possível depressão/ansiedade.
    """
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    audio_file = request.files["file"]

    filename = audio_file.filename
    if not filename:
        return jsonify({"error": "Nome de arquivo inválido ou ausente"}), 400

    try:
        audio_bytes = audio_file.read()

        result, status_code = process_consultation_audio(audio_bytes, filename)

        return jsonify(result), status_code

    except Exception as e:
        print(f"❌ [Audio Analysis Error]: {str(e)}")
        return jsonify(
            {"error": "Falha geral ao processar o áudio", "details": str(e)}
        ), 500


def analyze_womens_video():
    return jsonify({"message": "Pipeline de vídeo em construção"}), 200
