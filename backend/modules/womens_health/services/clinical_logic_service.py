def interpret_emotional_spectrum(spectrum: dict, exam_type: str):
    """
    Transforma números frios em perfis clínicos para o Maestro.
    """
    if exam_type == "VIDEO":
        sad = spectrum.get("sad", 0)
        fear = spectrum.get("fear", 0)
        angry = spectrum.get("angry", 0)
        happy = spectrum.get("happy", 0)
        disgust = spectrum.get("disgust", 0)

        # Matriz de Decisão EpiScope
        if fear > 0.4 and sad > 0.2:
            return "ALERTA: Traumatismo Emocional/Pavor"
        if angry > 0.4 and disgust > 0.2:
            return "ALERTA: Reatividade Aversiva (Possível Abuso)"
        if happy > 0.2 and (sad > 0.3 or fear > 0.3):
            return "ANOMALIA: Afeto Incongruente (Riso de Defesa)"
        if sad > 0.5:
            return "ESTADO: Melancolia Profunda"

        dominant_key = max(spectrum, key=lambda k: spectrum[k])
        return f"PREDOMINÂNCIA: {str(dominant_key).upper()}"

    return "PADRÃO_ESTÁVEL"
