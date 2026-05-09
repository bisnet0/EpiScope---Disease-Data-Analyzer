// src/features/DiagnosisWomensHealth/hooks/useLaparoscopyAnalyzer.ts
import { useState } from 'react';
import { useToast } from '@chakra-ui/react';
import { womensService } from '../services/womens-service';
import { type LaparoscopyAnalysisResponse } from '../types';

export const useLaparoscopyAnalyzer = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<LaparoscopyAnalysisResponse | null>(null);
  const toast = useToast();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setResult(null); // Limpa resultado anterior ao escolher novo vídeo
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast({
        title: 'Nenhum vídeo selecionado.',
        description: 'Por favor, selecione um vídeo cirúrgico para análise.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsAnalyzing(true);
    setResult(null);

    try {
      const data = await womensService.analyzeLaparoscopyVideo(selectedFile);
      setResult(data);
      toast({
        title: 'Análise Concluída',
        description: 'O modelo YOLO processou o vídeo cirúrgico com sucesso.',
        status: 'success',
        duration: 4000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Erro na Análise',
        description: error?.response?.data?.error || 'Falha ao processar o vídeo da cirurgia.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return {
    selectedFile,
    isAnalyzing,
    result,
    handleFileChange,
    handleAnalyze,
  };
};