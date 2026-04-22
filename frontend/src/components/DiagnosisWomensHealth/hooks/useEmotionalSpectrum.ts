import { useState, useCallback } from "react";
import { type AnalysisData } from "../types";

export const useEmotionalSpectrum = () => {
  const [spectrumData, setSpectrumData] = useState<AnalysisData | null>(null);

  const formatAndSetVideoResult = useCallback((rawResult: any) => {
    const formattedData: AnalysisData = {
      source_type: "video", // 👈 Marca como vídeo
      dominant_emotion: rawResult.video_analysis?.dominant_emotion || "neutral",
      emotional_blend: rawResult.clinical_profile || "PADRÃO_ESTÁVEL",
      emotion_distribution:
        rawResult.video_analysis?.emotion_distribution || {},
      total_frames_analyzed:
        rawResult.video_analysis?.total_frames_analyzed || 0,
    };

    setSpectrumData(formattedData);
  }, []);

  const formatAndSetAudioResult = useCallback((rawResult: any) => {
    const formattedData: AnalysisData = {
      source_type: "audio", // 👈 Marca como áudio
      emotional_blend: "ANÁLISE VOCAL",
      alerts: rawResult.alerts || [],
      clinical_insights: rawResult.clinical_insights || [],
      raw_features: rawResult.raw_features,
      transcription_snippet: rawResult.transcription_snippet,
    };

    setSpectrumData(formattedData);
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
