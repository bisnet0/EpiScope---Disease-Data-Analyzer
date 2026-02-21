import api from "../../../middleware/api";
import { GlaucomaGARunParams } from "../components/GlaucomaExperimentsPanel/types";

export const runGlaucomaGeneticOptimization = async (payload: GlaucomaGARunParams) => {
  const response = await api.post('/diagnose/glaucoma/optimize-ga', payload);
  return response.data;
};