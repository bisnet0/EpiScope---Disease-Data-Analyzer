import api from "../../../middleware/api";
import { type GlaucomaGARunParams } from "../types";

export const runGlaucomaGeneticOptimization = async (payload: GlaucomaGARunParams) => {
  const response = await api.post('glaucoma/diagnose/optimize-ga', payload);
  return response.data;
};