import { useState, useCallback } from 'react';
import { womensService } from '../services/womens-service';
import { type AnalysisStatus } from '../types';

export const useAudioAnalyzer = () => {
  const [audioStatus, setAudioStatus] = useState<AnalysisStatus>('idle');
  const [audioError, setAudioError] = useState<string | null>(null);

  const processAudio = useCallback(async (file: File, consultationType: string) => {
    setAudioStatus('analyzing');
    setAudioError(null);
    
    try {
      const response = await womensService.analyzeAudio(file, consultationType);
      setAudioStatus('success');
      return response.data; // Retorna os dados brutos
    } catch (err: any) {
      console.error('❌ Falha na API de Áudio:', err);
      const errorMessage = err.response?.data?.details || err.response?.data?.error || 'Erro de comunicação com o Dr. EpiScope.';
      setAudioError(errorMessage);
      setAudioStatus('error');
      throw err; 
    }
  }, []);

  const resetAudioState = useCallback(() => {
    setAudioStatus('idle');
    setAudioError(null);
  }, []);

  return { audioStatus, audioError, processAudio, resetAudioState };
};