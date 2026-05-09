import { useState, useEffect, useCallback } from "react";
import { womensService } from "../services/womens-service";
import {
  type CyclePredictionResponse,
  type CycleProfilePayload,
} from "../types";
import { useToast } from "../../Toast/components/ToastContext";

export const useCyclePredictor = () => {
  const { showToast } = useToast();
  const [prediction, setPrediction] = useState<CyclePredictionResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true); // Começa true para o loading inicial
  const [isUpdating, setIsUpdating] = useState(false);

  // Função para buscar a previsão cruzada com o Strava/Fit
  const fetchPrediction = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await womensService.getCyclePrediction();
      setPrediction(data);
    } catch (error: any) {
      showToast({
        title: "Erro de Sincronização",
        message:
          error?.response?.data?.error ||
          "Falha ao buscar os dados preditivos do ciclo.",
        type: "error",
      });
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  // Busca os dados automaticamente quando a tela é montada
  useEffect(() => {
    fetchPrediction();
  }, [fetchPrediction]);

  useEffect(() => {
    if (prediction?.maestro_recommendation && prediction.maestro_recommendation.includes("ALERTA")) {
      
      showToast({
        title: "Alerta de Severidade Ginecológica",
        message: "O Maestro identificou necessidade de conduta clínica urgente.",
        type: "info",
      });

      const event = new CustomEvent("openMaestroChat", {
        detail: {
          diagnosis: prediction.maestro_recommendation,
          consultationType: "PREDICAO_CICLO" // Contexto para a tool do backend
        },
      });
      window.dispatchEvent(event);
    }
  }, [prediction, showToast]);

  // Função para salvar as configurações e recalcular a previsão
  const updateProfile = async (payload: CycleProfilePayload) => {
    setIsUpdating(true);
    try {
      await womensService.updateCycleProfile(payload);
      showToast({
        title: "Perfil Preditivo Atualizado",
        message: "Os parâmetros do seu ciclo foram calibrados com sucesso.",
        type: "success",
      });

      // Assim que salva no banco, já puxa a nova previsão atualizada!
      await fetchPrediction();
      return true;
    } catch (error: any) {
      showToast({
        title: "Falha na Calibração",
        message:
          error?.response?.data?.error ||
          "Não foi possível salvar as configurações do ciclo.",
        type: "error",
      });
      return false;
    } finally {
      setIsUpdating(false);
    }
  };

  return {
    prediction,
    isLoading,
    isUpdating,
    updateProfile,
    refreshPrediction: fetchPrediction, // Útil se você quiser colocar um botão de "Forçar Sincronização" na tela
  };
};
