import api from "./api";
import { GARunParams } from "../components/ExperimentsPanel/types";

export const runManualExperimentApi = async (modelType: string, params: any) => {
  const response = await api.post('/diagnose/experiment', {
    model_type: modelType,
    params
  });
  return response.data;
};

export const getAdvisorSuggestionApi = async () => {
  const response = await api.get('/diagnose/advisor');
  return response.data;
};

export const runGeneticOptimizationApi = async (payload: GARunParams) => {
  const response = await api.post('/diagnose/optimize-ga', payload);
  return response.data;
};