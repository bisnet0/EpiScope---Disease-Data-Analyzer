import io
import librosa
import numpy as np

def process_consultation_audio(audio_bytes, filename):
    """
    Analisa o áudio buscando marcadores acústicos de depressão/ansiedade.
    - Tom de voz (Pitch/F0): Variações muito baixas (monotonia) podem indicar depressão.
    - Taxa de fala e pausas: Hesitações longas indicam ansiedade ou trauma.
    """
    print(f"🎙️ Iniciando análise de áudio: {filename}")
    
    try:
        # Librosa prefere ler de arquivos, então usamos io.BytesIO para simular um arquivo em memória
        audio_stream = io.BytesIO(audio_bytes)
        
        # Carrega o áudio. sr=None preserva a taxa de amostragem original
        y, sr = librosa.load(audio_stream, sr=None)
        
        # 1. Analisando Pausas e Hesitação (Energia do áudio)
        # Dividimos o áudio em intervalos de silêncio e fala
        non_mute_intervals = librosa.effects.split(y, top_db=30)
        
        total_duration = librosa.get_duration(y=y, sr=sr)
        speech_duration = sum([(end - start) / sr for start, end in non_mute_intervals])
        silence_duration = total_duration - speech_duration
        
        silence_ratio = silence_duration / total_duration if total_duration > 0 else 0

        # 2. Analisando o Tom (Pitch)
        # Extrai a frequência fundamental (F0)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Filtra os pitches válidos (maiores que 0)
        valid_pitches = pitches[magnitudes > np.median(magnitudes)]
        valid_pitches = valid_pitches[valid_pitches > 0]
        
        if len(valid_pitches) > 0:
            mean_pitch = np.mean(valid_pitches)
            pitch_variation = np.std(valid_pitches) # Desvio padrão: indica se a voz está monótona
        else:
            mean_pitch = 0
            pitch_variation = 0

        # 3. Lógica de Triagem (Regras baseadas em marcadores acústicos)
        # Uma voz muito monótona (baixa variação de pitch) e com muito silêncio (hesitação) liga um alerta.
        anxiety_markers = []
        needs_attention = False
        
        if silence_ratio > 0.40: # Mais de 40% do áudio é silêncio/pausa
            anxiety_markers.append("Alta taxa de hesitação/pausas prolongadas")
            needs_attention = True
            
        if pitch_variation < 20 and mean_pitch > 0: # Voz muito "reta"
            anxiety_markers.append("Achatamento afetivo (voz monótona)")
            needs_attention = True

        response = {
            "success": True,
            "filename": filename,
            "duration_seconds": round(total_duration, 2),
            "analysis_details": {
                "silence_ratio_percentage": round(silence_ratio * 100, 2),
                "pitch_variation_hz": round(float(pitch_variation), 2),
                "acoustic_markers": anxiety_markers
            },
            "clinical_insight": "Sinais acústicos indicativos de fadiga ou sofrimento psicológico detectados." if needs_attention else "Padrões vocais dentro da normalidade.",
            "needs_emergency": needs_attention # Isso vai triggar o Maestro depois!
        }
        
        return response, 200

    except Exception as e:
        print(f"❌ Erro na extração de features do Librosa: {str(e)}")
        return {"error": "Falha no processamento do sinal de áudio", "details": str(e)}, 500