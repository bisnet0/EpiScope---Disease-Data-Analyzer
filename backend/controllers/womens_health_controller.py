from flask import request, jsonify
from backend.services.audio_analysis_service import process_consultation_audio
# from backend.services.video_analysis_service import process_surgery_video (faremos depois)

def analyze_womens_audio():
    """
    Recebe um arquivo de áudio de uma consulta (ex: acompanhamento pós-parto)
    e analisa sinais de hesitação, tom de voz e possível depressão/ansiedade.
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400
        
    audio_file = request.files['file']
    
    if audio_file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    try:
        # Lê os bytes do arquivo em memória para não precisar salvar no disco à toa
        audio_bytes = audio_file.read()
        
        # Chama o serviço pesado de ML
        result, status_code = process_consultation_audio(audio_bytes, audio_file.filename)
        
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [Audio Analysis Error]: {str(e)}")
        return jsonify({"error": "Falha ao processar o áudio", "details": str(e)}), 500

def analyze_womens_video():
    # Deixando o esqueleto pronto para a próxima sprint!
    return jsonify({"message": "Pipeline de vídeo em construção"}), 200