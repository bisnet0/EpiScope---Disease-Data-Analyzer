import { useState, useCallback } from 'react';
import { womensService } from '../services/womens-service';
import { type AnalysisStatus } from '../types';

export const useVideoAnalyzer = () => {
  const [videoStatus, setVideoStatus] = useState<AnalysisStatus>('idle');
  const [videoError, setVideoError] = useState<string | null>(null);

  const processVideo = useCallback(async (file: File, consultationType: string) => {
    setVideoStatus('analyzing');
    setVideoError(null);
    
    try {
      const response = await womensService.analyzeVideo(file, consultationType);
      setVideoStatus('success');
      return response.data; // Retorna os dados brutos para o Módulo orquestrar
    } catch (err: any) {
      console.error('❌ Falha na API de Vídeo:', err);
      const errorMessage = err.response?.data?.details || err.response?.data?.error || 'Erro de comunicação com o Dr. EpiScope.';
      setVideoError(errorMessage);
      setVideoStatus('error');
      throw err; 
    }
  }, []);

  const resetVideoState = useCallback(() => {
    setVideoStatus('idle');
    setVideoError(null);
  }, []);

  return { videoStatus, videoError, processVideo, resetVideoState };
};