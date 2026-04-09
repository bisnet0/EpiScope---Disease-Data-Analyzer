import os

# 👇 A vacina contra o congelamento do Flask + HuggingFace (Rust Tokenizers)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import io
import numpy as np
import librosa  # type: ignore
from transformers import pipeline  # type: ignore
from pydub import AudioSegment  # type: ignore

# Variáveis globais limpas
_transcriber = None
_whisper_load_failed = False


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
    Usa Librosa para extrair matemática pura da voz da paciente.
    Passamos o io.BytesIO para evitar que o Librosa tente invocar o FFmpeg desnecessariamente.
    """
    try:
        # Usamos soundfile como backend primário, que é mais leve e não pede FFmpeg para WAV
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
    except Exception as e:
        print(f"⚠️ Erro no carregamento padrão: {e}. Tentando fallback...")
        # Se falhar (ex: codec estranho), tentamos forçar via pydub que já converteu
        audio_stream = io.BytesIO(audio_bytes)
        y, sr = librosa.load(audio_stream, sr=16000)

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
    audio_bytes: bytes, filename: str, consultation_type: str, audio_language: str
):
    """
    Pipeline completo: Formata + Extrai Acústica + Transcreve + Aplica Regras Clínicas
    """
    print(f"\n🎙️ [WOMENS HEALTH] Analisando {filename} | Contexto: {consultation_type}")

    try:
        # 0. FORÇA O FORMATO WAV PARA NÃO QUEBRAR O LIBROSA
        safe_audio_bytes = force_wav_format(audio_bytes, filename)

        print("📊 Extraindo features acústicas (Librosa)...")
        # Usamos o safe_audio_bytes aqui
        features = extract_acoustic_features(safe_audio_bytes)

        transcription = "Transcrição indisponível."

        # 👇 Chama o nosso carregamento inteligente aqui
        ai_transcriber = get_transcriber()

        if ai_transcriber is not None:
            print(f"📝 Transcrevendo áudio com Whisper (Idioma: {audio_language})...")

            # Mapeamento dos idiomas enviados pelo front
            lang_map = {
                "pt": "portuguese",
                "en": "english",
                "es": "spanish",
                "de": "german",
                "ja": "japanese",
                "it": "italian",
            }

            # Lógica de "adivinhação" ou idioma forçado
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
                diagnosis_result["clinical_insights"].append(
                    "Nenhum alerta de hipervigilância ativado com base no áudio cru."
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
