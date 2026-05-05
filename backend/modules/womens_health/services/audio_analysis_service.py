import os
import io
import joblib
import numpy as np
import librosa  # type: ignore
from transformers import pipeline  # type: ignore
from pydub import AudioSegment  # type: ignore

# 👇 A vacina contra o congelamento do Flask + HuggingFace (Rust Tokenizers)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "audio_distress_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "models", "audio_scaler.pkl")

# Variáveis globais limpas
_transcriber = None
_whisper_load_failed = False
_audio_model = None
_audio_scaler = None


def load_audio_ml_models():
    """Carrega a Random Forest treinada para detectar coação na voz"""
    global _audio_model, _audio_scaler
    if _audio_model is None and os.path.exists(MODEL_PATH):
        try:
            _audio_model = joblib.load(MODEL_PATH)
            _audio_scaler = joblib.load(SCALER_PATH)
            print(
                "✅ [AUDIO SERVICE] Modelo de Machine Learning carregado com sucesso!"
            )
        except Exception as e:
            print(f"⚠️ [AUDIO SERVICE] Erro ao carregar modelo ML: {e}")


def get_transcriber():
    global _transcriber, _whisper_load_failed

    # Só tenta carregar se for None E se não tiver falhado antes
    if _transcriber is None and not _whisper_load_failed:
        print("\n⏳ Carregando modelo Whisper-Tiny para transcrição (Lazy Load)...")
        try:
            _transcriber = pipeline(
                "automatic-speech-recognition", model="openai/whisper-tiny"
            )
            print("✅ Whisper carregado com sucesso!")
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível carregar o Whisper: {e}")
            _whisper_load_failed = True  # Registramos a falha na flag, não no modelo!

    return _transcriber


def force_wav_format(audio_bytes: bytes, filename: str) -> bytes:
    """
    Pega qualquer formato de áudio (mp3, webm, ogg) e converte
    para um WAV limpo em memória para o Librosa não chorar.
    """
    ext = filename.split(".")[-1].lower() if "." in filename else "mp3"

    # Se já for WAV, passa direto
    if ext == "wav":
        return audio_bytes

    print(f"🔄 Convertendo {ext.upper()} para WAV em memória...")
    audio_stream = io.BytesIO(audio_bytes)

    try:
        audio = AudioSegment.from_file(audio_stream, format=ext)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        return wav_io.getvalue()
    except Exception as e:
        print(
            f"⚠️ Aviso: Falha ao forçar WAV, tentando seguir com o original. Erro: {e}"
        )
        return audio_bytes


def extract_acoustic_features(audio_bytes: bytes):
    """
    Usa Librosa para extrair matemática pura da voz da paciente e as ML Features.
    """
    try:
        # Usamos soundfile como backend primário
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
    except Exception as e:
        print(f"⚠️ Erro no carregamento padrão: {e}. Tentando fallback...")
        audio_stream = io.BytesIO(audio_bytes)
        y, sr = librosa.load(audio_stream, sr=16000)

    # 👇 1. Extração para o Modelo ML (13 MFCCs + 1 RMS)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    rms_features = librosa.feature.rms(y=y)
    ml_features = np.hstack((np.mean(mfccs.T, axis=0), np.mean(rms_features))).reshape(
        1, -1
    )

    # 2. Extração crua (Heurísticas visuais para o Front)
    mean_volume = float(np.mean(rms_features))

    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_variance = float(np.var(pitches[pitches > 0])) if np.any(pitches > 0) else 0.0

    non_mute_intervals = librosa.effects.split(y, top_db=20)
    total_audio_duration = librosa.get_duration(y=y, sr=sr)
    non_mute_duration = sum([(end - start) / sr for start, end in non_mute_intervals])
    silence_duration = total_audio_duration - non_mute_duration

    hesitation_ratio = (
        silence_duration / total_audio_duration if total_audio_duration > 0 else 0
    )

    return {
        "ml_features": ml_features,
        "raw_metrics": {
            "mean_volume": mean_volume,
            "pitch_variance": pitch_variance,
            "hesitation_ratio": hesitation_ratio,
            "total_duration_sec": total_audio_duration,
        },
    }


def process_consultation_audio(
    audio_bytes: bytes, filename: str, consultation_type: str, audio_language: str
):
    """
    Pipeline completo: Formata + Extrai Acústica ML + Transcreve + Aplica Maestro RAG
    """
    print(f"\n🎙️ [WOMENS HEALTH] Analisando {filename} | Contexto: {consultation_type}")

    try:
        # Carrega os pesos da Random Forest
        load_audio_ml_models()

        # 0. FORÇA O FORMATO WAV PARA NÃO QUEBRAR O LIBROSA
        safe_audio_bytes = force_wav_format(audio_bytes, filename)

        print("📊 Extraindo features acústicas...")
        extraction = extract_acoustic_features(safe_audio_bytes)
        features = extraction["raw_metrics"]
        ml_features = extraction["ml_features"]

        transcription = "Transcrição indisponível."

        # Transcrição com Whisper
        ai_transcriber = get_transcriber()

        if ai_transcriber is not None:
            print(f"📝 Transcrevendo áudio com Whisper (Idioma: {audio_language})...")

            lang_map = {
                "pt": "portuguese",
                "en": "english",
                "es": "spanish",
                "de": "german",
                "ja": "japanese",
                "it": "italian",
            }

            if audio_language == "auto":
                result = ai_transcriber(safe_audio_bytes)
            else:
                whisper_lang = lang_map.get(audio_language, "portuguese")
                result = ai_transcriber(
                    safe_audio_bytes, generate_kwargs={"language": whisper_lang}
                )

            if isinstance(result, list) and len(result) > 0:
                transcription = result[0].get("text", "")
            elif isinstance(result, dict):
                transcription = result.get("text", "")

            print(f"🗣️ Texto detectado: '{transcription[:50]}...'")

        diagnosis_result = {
            "status": "success",
            "file": filename,
            "consultation_context": consultation_type,
            "raw_features": features,
            "transcription_snippet": transcription,
            "clinical_insights": [],
            "alerts": [],
        }

        vol = features["mean_volume"]
        hesitation = features["hesitation_ratio"]
        pitch_var = features["pitch_variance"]

        # 👇 INFERÊNCIA DO MODELO DE MACHINE LEARNING
        ml_alert_message = None
        if _audio_model and _audio_scaler:
            features_scaled = _audio_scaler.transform(ml_features)
            prediction = _audio_model.predict(features_scaled)[0]
            prob = _audio_model.predict_proba(features_scaled)[0][1]

            if prediction == 1 or prob > 0.65:
                ml_alert_message = f"🚨 ALERTA ML: Padrão acústico de Coação/Risco detectado (Confiança: {prob * 100:.1f}%)"
                diagnosis_result["alerts"].append(ml_alert_message)
                diagnosis_result["clinical_insights"].append(
                    "O modelo de IA identificou marcadores consistentes com supressão de emoções ou hesitação severa."
                )
            else:
                diagnosis_result["clinical_insights"].append(
                    f"Vocalização estável segundo o modelo ML (Confiança: {(1 - prob) * 100:.1f}%)."
                )
        else:
            # Fallback (heurística) caso o arquivo .pkl não seja encontrado
            if consultation_type == "TRIAGEM_VIOLENCIA" and (
                vol < 0.01 and hesitation > 0.30
            ):
                ml_alert_message = "🚨 ALERTA HEURÍSTICO: Volume sussurrado e alta hesitação detectados."
                diagnosis_result["alerts"].append(ml_alert_message)

        # 👇 INTEGRAÇÃO COM O MAESTRO (Enviando o Alerta da IA para forçar o uso do RAG)
        from backend.modules.core_agent.controllers.workflow_controller import (
            run_hospital_workflow_internal,
        )

        print(f"🧠 [WOMENS HEALTH]: Enviando transcrição e métricas para o Maestro...")

        maestro_payload = {
            "context": "WOMENS_HEALTH_AUDIO_ANALYSIS",
            "consultation_type": consultation_type,
            "transcription": transcription,
            "machine_learning_alert": ml_alert_message,
            "acoustic_metrics": {
                "hesitation_level": "ALTA" if hesitation > 0.3 else "NORMAL",
                "volume_level": "SUSSURRADO" if vol < 0.01 else "NORMAL",
                "pitch_stability": "INSTÁVEL" if pitch_var > 1000 else "ESTÁVEL",
            },
            "raw_features": features,
        }

        maestro_res = run_hospital_workflow_internal(maestro_payload)

        if isinstance(maestro_res, dict):
            diagnosis_result["maestro_analysis"] = maestro_res.get(
                "clinical_report", "Análise indisponível"
            )
            diagnosis_result["recommended_actions"] = maestro_res.get("next_steps", [])
            diagnosis_result["priority_score"] = maestro_res.get("priority", "MEDIUM")

        # Regras secundárias
        if consultation_type == "POS_PARTO" and hesitation > 0.40 and pitch_var < 100:
            diagnosis_result["alerts"].append(
                "⚠️ ALERTA: Forte indicativo acústico de Depressão Pós-Parto."
            )
        elif consultation_type == "PRE_NATAL" and hesitation < 0.15 and pitch_var > 500:
            diagnosis_result["alerts"].append(
                "⚠️ ALERTA: Possível Ansiedade Gestacional Severa."
            )

        print("✅ [WOMENS HEALTH] Pipeline de áudio ML concluído com sucesso.")
        return diagnosis_result, 200

    except Exception as e:
        print(f"❌ [WOMENS HEALTH ERROR]: {str(e)}")
        return {"error": "Falha na análise", "details": str(e)}, 500
