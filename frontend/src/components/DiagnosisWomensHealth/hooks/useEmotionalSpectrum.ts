import { useState, useCallback } from "react";
import { type AnalysisData } from "../types";
import { useToast } from "../../Toast/components/ToastContext";

export const useEmotionalSpectrum = () => {
  const [spectrumData, setSpectrumData] = useState<AnalysisData | null>(null);

  const { showToast } = useToast();
  const triggerMaestroAlert = (reason: string, consultationType: string) => {
    const event = new CustomEvent("openMaestroChat", {
      detail: {
        diagnosis: reason,
        consultationType: consultationType,
      },
    });
    window.dispatchEvent(event);
  };

  const formatAndSetVideoResult = useCallback((rawResult: any) => {
    const dominant = rawResult.video_analysis?.dominant_emotion || "neutral";

    const formattedData: AnalysisData = {
      source_type: "video",
      dominant_emotion: dominant,
      emotional_blend: rawResult.clinical_profile || "PADRÃO_ESTÁVEL",
      emotion_distribution:
        rawResult.video_analysis?.emotion_distribution || {},
      total_frames_analyzed:
        rawResult.video_analysis?.total_frames_analyzed || 0,
    };

    setSpectrumData(formattedData);

    if (["fear", "sad"].includes(dominant)) {
      triggerMaestroAlert(
        `Microexpressões indicam sofrimento ou medo (${dominant.toUpperCase()}).`,
        rawResult.video_analysis?.consultation_context ||
          rawResult.consultation_context ||
          "TRIAGEM_VIOLENCIA",
      );
      showToast({
        message: `Microexpressões indicam sofrimento ou medo (${dominant.toUpperCase()}). Alerta enviado para o Maestro.`,
        type: "info",
        title: "Alerta de Microexpressão",
      });
    }
  }, []);

  const formatAndSetAudioResult = useCallback((rawResult: any) => {
    const alerts = rawResult.alerts || [];

    const formattedData: AnalysisData = {
      source_type: "audio",
      emotional_blend: "ANÁLISE VOCAL",
      alerts: alerts,
      clinical_insights: rawResult.clinical_insights || [],
      raw_features: rawResult.raw_features,
      transcription_snippet: rawResult.transcription_snippet,
    };

    setSpectrumData(formattedData);

    if (alerts.length > 0) {
      triggerMaestroAlert(
        "Anomalias vocais detectadas (Hesitação/Volume atípico)",
        rawResult.consultation_context || "TRIAGEM_VIOLENCIA",
      );
    }
    showToast({
      message: `Anomalias vocais detectadas (Hesitação/Volume atípico). O áudio contém indícios de estresse ou coação. Alerta enviado para o Maestro.`,
      type: "info",
      title: "Alerta de Análise Vocal",
    });
  }, []);

  const clearSpectrum = useCallback(() => {
    setSpectrumData(null);
  }, []);

  return {
    spectrumData,
    formatAndSetVideoResult,
    formatAndSetAudioResult,
    clearSpectrum,
  };
};
