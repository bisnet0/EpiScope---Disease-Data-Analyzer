// src/features/DiagnosisWomensHealth/hooks/useLaparoscopyAnalyzer.ts
import { useState } from "react";
import { womensService } from "../services/womens-service";
import { type LaparoscopyAnalysisResponse } from "../types";
import { useToast } from "../../Toast/components/ToastContext";

export const useLaparoscopyAnalyzer = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<LaparoscopyAnalysisResponse | null>(
    null,
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setResult(null); // Limpa resultado anterior ao escolher novo vídeo
    }
  };
  const { showToast } = useToast();

  const handleAnalyze = async () => {
    if (!selectedFile) {
      showToast({
        title: "Nenhum vídeo selecionado.",
        message: "Por favor, selecione um vídeo de laparoscopia para análise.",
        type: "info",
      });
      return;
    }

    setIsAnalyzing(true);
    setResult(null);

    try {
      const data = await womensService.analyzeLaparoscopyVideo(selectedFile);
      setResult(data);
      showToast({
        title: "Análise Concluída",
        message: "Análise Concluída",
        type: "success",
      });
    } catch (error: any) {
      showToast({
        title: "Erro na Análise",
        message:
          error.response?.data?.error ||
          "Ocorreu um erro durante a análise do vídeo.",
        type: "error",
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
