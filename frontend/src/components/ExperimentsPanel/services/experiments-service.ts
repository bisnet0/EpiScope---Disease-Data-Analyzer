import api from "../../../middleware/api";
import { type GARunParams } from "../types";

export const runManualExperimentApi = async (modelType: string, params: any) => {
  const response = await api.post('laboratory/diagnose/experiment', {
    model_type: modelType,
    params
  });
  return response.data;
};

export const getAdvisorSuggestionApi = async () => {
  const response = await api.get('laboratory/diagnose/advisor');
  return response.data;
};

export const runGeneticOptimizationApi = async (payload: GARunParams) => {
  const response = await api.post('arbovirus/diagnose/optimize-ga', payload);
  return response.data;
};