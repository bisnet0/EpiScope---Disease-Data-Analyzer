import os
import uuid
from flask import request, jsonify

VIDEO_TEMP_DIR = "temp_videos"
os.makedirs(VIDEO_TEMP_DIR, exist_ok=True)
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
    """
    Endpoint para análise de vídeo e microexpressões faciais.
    """
    # Lazy Import para manter o boot do Flask rápido!
    from backend.modules.womens_health.services.video_service import process_womens_video

    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo de vídeo enviado"}), 400
        
    video_file = request.files['file']
    # Geramos um nome único para evitar colisão no container
    temp_filename = f"{uuid.uuid4()}_{video_file.filename}"
    video_path = os.path.join(VIDEO_TEMP_DIR, temp_filename)
    
    try:
        # Salva o vídeo temporariamente no disco do container
        video_file.save(video_path)
        
        # Chama o processamento pesado
        analysis_result = process_womens_video(video_path)
        
        # Limpeza: Removemos o arquivo após a análise
        if os.path.exists(video_path):
            os.remove(video_path)
            
        return jsonify({
            "status": "success",
            "video_analysis": analysis_result
        }), 200

    except Exception as e:
        if os.path.exists(video_path): os.remove(video_path)
        print(f"❌ [VIDEO ERROR]: {str(e)}")
        return jsonify({"error": "Falha no processamento de vídeo", "details": str(e)}), 500
