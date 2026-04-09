from flask import request, jsonify


def analyze_womens_audio():
    """
    Recebe um arquivo de áudio e analisa sinais clínicos.
    """

    from backend.modules.womens_health.services.audio_analysis_service import (
        process_consultation_audio,
    )

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    audio_file = request.files["file"]
    filename = audio_file.filename

    consultation_type = request.form.get("consultation_type", "GINECOLOGICA")

    audio_language = request.form.get("language", "auto")

    if not filename:
        return jsonify({"error": "Nome de arquivo inválido ou ausente"}), 400

    try:
        audio_bytes = audio_file.read()

        result, status_code = process_consultation_audio(
            audio_bytes, filename, consultation_type, audio_language
        )

        return jsonify(result), status_code

    except Exception as e:
        print(f"❌ [Audio Analysis Error]: {str(e)}")
        return jsonify(
            {"error": "Falha geral ao processar o áudio", "details": str(e)}
        ), 500


def analyze_womens_video():
    return jsonify({"message": "Pipeline de vídeo em construção"}), 200
