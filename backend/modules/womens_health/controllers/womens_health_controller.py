import os
import uuid
from flask import request, jsonify


VIDEO_TEMP_DIR = "temp_videos"
os.makedirs(VIDEO_TEMP_DIR, exist_ok=True)


def analyze_womens_audio():
    """
    Recebe um arquivo de áudio e analisa sinais clínicos,
    salvando o resultado no banco para auditoria e cruzamento multimodal.
    """
    from backend.modules.womens_health.services.audio_analysis_service import (
        process_consultation_audio,
    )

    from backend.modules.womens_health.models.womens_models import WomensHealthAnalysis
    from backend.modules.auth.models.user_model import db
    from flask_jwt_extended import (
        get_jwt_identity,
    )

    current_user_id = get_jwt_identity()

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

        if status_code == 200 and result.get("status") == "success":
            alerts = result.get("alerts", [])
            insights = result.get("clinical_insights", [])

            dominant_profile = "ANÁLISE VOCAL ESTÁVEL"
            if alerts:
                dominant_profile = (
                    f"ALERTA VOCAL: {len(alerts)} anomalia(s) detectada(s)"
                )
            elif insights:
                dominant_profile = "INSIGHTS VOCAIS DETECTADOS"

            raw_features = result.get("raw_features", {})
            if not isinstance(raw_features, dict):
                raw_features = {}

            transcription_snippet = result.get("transcription_snippet", "")
            if not isinstance(transcription_snippet, str):
                transcription_snippet = str(transcription_snippet)

            new_analysis = WomensHealthAnalysis(
                exam_type="AUDIO",
                patient_id=current_user_id,
                consultation_type=consultation_type,
                dominant_result=dominant_profile,
                raw_data=raw_features,
                transcription=transcription_snippet,
            )

            try:
                db.session.add(new_analysis)
                db.session.commit()
            except Exception as db_error:
                db.session.rollback()
                print(f"❌ [DB ERROR]: {str(db_error)}")
                raise db_error

            result["analysis_id"] = new_analysis.id

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

    from backend.modules.womens_health.services.video_service import (
        process_womens_video,
    )
    from backend.modules.womens_health.services.clinical_logic_service import (
        interpret_emotional_spectrum,
    )
    from backend.modules.womens_health.models.womens_models import WomensHealthAnalysis
    from backend.modules.auth.models.user_model import db
    from flask_jwt_extended import (
        get_jwt_identity,
    )

    current_user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo de vídeo enviado"}), 400

    video_file = request.files["file"]
    temp_filename = f"{uuid.uuid4()}_{video_file.filename}"
    video_path = os.path.join(VIDEO_TEMP_DIR, temp_filename)

    try:
        video_file.save(video_path)

        analysis_result = process_womens_video(video_path)

        if analysis_result.get("status") == "error":
            if os.path.exists(video_path):
                os.remove(video_path)
            return jsonify(analysis_result), 400

        raw_spectrum = analysis_result.get("emotion_distribution", {})

        if not isinstance(raw_spectrum, dict):
            spectrum = {}
        else:
            spectrum = raw_spectrum

        clinical_profile = interpret_emotional_spectrum(spectrum, "VIDEO")

        new_analysis = WomensHealthAnalysis(
            exam_type="VIDEO",
            patient_id=current_user_id,
            consultation_type=request.form.get("consultation_type", "GENERAL"),
            dominant_result=clinical_profile,
            raw_data=spectrum,
        )

        try:
            db.session.add(new_analysis)
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            print(f"❌ [DB ERROR]: {str(db_error)}")
            raise db_error

        if os.path.exists(video_path):
            os.remove(video_path)

        return jsonify(
            {
                "status": "success",
                "analysis_id": new_analysis.id,
                "clinical_profile": clinical_profile,
                "video_analysis": analysis_result,
            }
        ), 200

    except Exception as e:
        if os.path.exists(video_path):
            os.remove(video_path)
        print(f"❌ [VIDEO ERROR]: {str(e)}")
        return jsonify(
            {"error": "Falha no processamento de vídeo", "details": str(e)}
        ), 500


def get_integrated_report():
    """
    Retorna o laudo consolidado cruzando áudio e vídeo.
    """
    from backend.modules.womens_health.services.womens_orchestrator_service import (
        get_integrated_health_report,
    )
    from flask import request

    consultation_type = request.args.get("consultation_type", "GENERAL")
    patient_id = request.args.get("patient_id", type=int)

    try:
        report = get_integrated_health_report(
            patient_id=patient_id, consultation_type=consultation_type
        )

        return jsonify(report), 200
    except Exception as e:
        print(f"❌ [REPORT ERROR]: {str(e)}")
        return jsonify(
            {"error": "Falha ao gerar relatório integrado", "details": str(e)}
        ), 500


def analyze_laparoscopy_video():
    """
    Endpoint dedicado para análise de cirurgias ginecológicas usando YOLOv8.
    Verifica presença de instrumentos e sangramento anômalo.
    """
    import os
    import uuid
    from flask import request, jsonify
    from flask_jwt_extended import get_jwt_identity
    from werkzeug.utils import secure_filename

    from backend.modules.womens_health.services.laparoscopy_service import (
        process_laparoscopy_video,
    )
    from backend.modules.womens_health.models.womens_models import WomensHealthAnalysis
    from backend.modules.auth.models.user_model import db

    current_user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo de vídeo enviado"}), 400

    video_file = request.files["file"]

    if not video_file.filename:
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    safe_original_name = video_file.filename or "cirurgia_laparo.mp4"

    filename = secure_filename(safe_original_name)
    temp_filename = f"laparo_{uuid.uuid4()}_{filename}"
    video_path = os.path.join(VIDEO_TEMP_DIR, temp_filename)

    try:
        video_file.save(video_path)

        analysis_result = process_laparoscopy_video(video_path)

        if analysis_result.get("status") == "error":
            if os.path.exists(video_path):
                os.remove(video_path)
            return jsonify(analysis_result), 400

        clinical_alerts = analysis_result.get("clinical_alerts", [])
        dominant_profile = "CIRURGIA DENTRO DA NORMALIDADE"

        if clinical_alerts:
            dominant_profile = (
                f"ALERTA CIRÚRGICO: {len(clinical_alerts)} anomalia(s) detectada(s)"
            )

        raw_data = {
            "items_detected": analysis_result.get("items_detected", {}),
            "bleeding_ratio": analysis_result.get("bleeding_ratio", 0.0),
        }

        new_analysis = WomensHealthAnalysis(
            exam_type="LAPAROSCOPY_VIDEO",
            patient_id=current_user_id,
            consultation_type="CIRURGIA_GINECOLOGICA",
            dominant_result=dominant_profile,
            raw_data=raw_data,
        )

        try:
            db.session.add(new_analysis)
            db.session.commit()
            analysis_result["analysis_id"] = new_analysis.id
        except Exception as db_error:
            db.session.rollback()
            print(f"❌ [DB ERROR]: {str(db_error)}")

            analysis_result["db_error"] = "Aviso: Não foi possível salvar o histórico."

        if os.path.exists(video_path):
            os.remove(video_path)

        return jsonify(analysis_result), 200

    except Exception as e:
        if os.path.exists(video_path):
            os.remove(video_path)
        print(f"❌ [LAPAROSCOPY ERROR]: {str(e)}")
        return jsonify(
            {
                "error": "Falha no processamento da cirurgia laparoscópica",
                "details": str(e),
            }
        ), 500
