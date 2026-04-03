import io
import numpy as np
import librosa # type: ignore
from transformers import pipeline


print("⏳ Carregando modelo Whisper-Tiny para transcrição...")
try:
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível carregar o Whisper: {e}")
    transcriber = None


def extract_acoustic_features(audio_bytes: bytes):
    """
    Usa Librosa para extrair matemática pura da voz da paciente.
    """

    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

    rms = librosa.feature.rms(y=y)
    mean_volume = float(np.mean(rms))

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
        "mean_volume": mean_volume,
        "pitch_variance": pitch_variance,
        "hesitation_ratio": hesitation_ratio,
        "total_duration_sec": total_audio_duration,
    }


def process_consultation_audio(
    audio_bytes: bytes, filename: str, consultation_type: str
):
    """
    Pipeline completo: Extrai Acústica + Transcreve + Aplica Regras Clínicas
    """
    print(f"\n🎙️ [WOMENS HEALTH] Analisando {filename} | Contexto: {consultation_type}")

    try:
        print("📊 Extraindo features acústicas (Librosa)...")
        features = extract_acoustic_features(audio_bytes)

        transcription = "Transcrição indisponível."
        if transcriber:
            print("📝 Transcrevendo áudio com Whisper...")
            result = transcriber(audio_bytes)

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

        if consultation_type == "POS_PARTO":
            if hesitation > 0.40 and pitch_var < 100:
                diagnosis_result["alerts"].append(
                    "⚠️ ALERTA: Voz monótona e alta hesitação. Forte indicativo de Depressão Pós-Parto."
                )
                diagnosis_result["clinical_insights"].append(
                    "A paciente apresenta pausas longas e pouca variação de tom, sugerindo apatia/disforia."
                )
            else:
                diagnosis_result["clinical_insights"].append(
                    "Padrão vocal dentro da normalidade para o puerpério."
                )

        elif consultation_type == "PRE_NATAL":
            if hesitation < 0.15 and pitch_var > 500:
                diagnosis_result["alerts"].append(
                    "⚠️ ALERTA: Padrão vocal acelerado e alta variação. Possível Ansiedade Gestacional Severa."
                )
                diagnosis_result["clinical_insights"].append(
                    "Identificada taquilalia (fala rápida) e tensão vocal aguda."
                )
            else:
                diagnosis_result["clinical_insights"].append(
                    "Sem sinais agudos de ansiedade gestacional pela voz."
                )

        elif consultation_type == "TRIAGEM_VIOLENCIA":
            if vol < 0.01 and hesitation > 0.30:
                diagnosis_result["alerts"].append(
                    "🚨 PROTOCOLO DE ACOLHIMENTO: Volume sussurrado e hesitação atípica detectados."
                )
                diagnosis_result["clinical_insights"].append(
                    "O padrão de fala sugere estado de hipervigilância, medo ou esquiva em relatar fatos."
                )

        else:
            if hesitation > 0.35:
                diagnosis_result["clinical_insights"].append(
                    "A paciente apresenta hesitação ao relatar o quadro. Recomenda-se abordagem acolhedora para queixas de dor pélvica."
                )
            else:
                diagnosis_result["clinical_insights"].append(
                    "Relato fluido, indicando conforto com o ambiente clínico."
                )

        print("✅ [WOMENS HEALTH] Pipeline de áudio concluído com sucesso.")
        return diagnosis_result, 200

    except Exception as e:
        print(f"❌ [WOMENS HEALTH ERROR]: {str(e)}")
        return {"error": "Falha na análise", "details": str(e)}, 500
