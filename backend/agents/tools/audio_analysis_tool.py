from langchain.tools import tool
import json

@tool("audio_clinical_analysis_tool")
def audio_clinical_analysis_tool(analysis_json: str) -> str:
    """
    Use esta ferramenta OBRIGATORIAMENTE quando receber dados de análise de áudio (voz) de uma paciente.
    A entrada deve ser uma string JSON contendo 'silence_ratio_percentage', 'pitch_variation_hz' e 'acoustic_markers'.
    A ferramenta retorna uma interpretação clínica focada em saúde mental da mulher (Depressão Pós-Parto, Ansiedade ou Trauma).
    """
    try:
        data = json.loads(analysis_json)
        silence_ratio = data.get("silence_ratio_percentage", 0)
        pitch_variation = data.get("pitch_variation_hz", 0)
        markers = data.get("acoustic_markers", [])
        
        interpretation = "📋 **Laudo de Biomarcadores Vocais (Saúde da Mulher)**\n\n"
        
        # Interpretando a hesitação (Silêncio)
        if silence_ratio > 40:
            interpretation += "⚠️ **Alta Hesitação (Silêncio > 40%):** A paciente apresenta pausas prolongadas na fala. Clinicamente, isso pode indicar ansiedade severa, dificuldade de verbalizar traumas (violência doméstica) ou lentidão cognitiva associada à depressão pós-parto.\n"
        else:
            interpretation += "✅ **Fluência Normal:** Taxa de hesitação dentro dos limites normais.\n"
            
        # Interpretando a monotonia (Pitch)
        if pitch_variation < 20 and pitch_variation > 0:
            interpretation += "⚠️ **Achatamento Afetivo (Baixa variação de tom):** A voz monótona é um forte biomarcador de depressão pós-parto, anedonia ou fadiga hormonal extrema.\n"
        elif pitch_variation >= 20:
            interpretation += "✅ **Modulação Vocal:** Variação de tom adequada, sem sinais de achatamento afetivo.\n"
            
        # Alertas do sistema base
        if markers:
            interpretation += f"\n🚨 **Alertas do Sistema:** {', '.join(markers)}\n"
            interpretation += "\n**Diretriz Sugerida pelo Maestro:** Recomenda-se aplicação imediata da Escala de Depressão Pós-Parto de Edimburgo (EPDS) e, se necessário, acolhimento psicológico de urgência."
        else:
            interpretation += "\n**Conclusão:** Não foram detectados biomarcadores vocais de risco agudo. Manter acompanhamento de rotina."

        return interpretation

    except json.JSONDecodeError:
        return "Erro: A entrada fornecida não é um JSON válido. Certifique-se de passar os dados de análise de áudio corretamente."
    except Exception as e:
        return f"Erro interno na ferramenta de análise acústica: {str(e)}"