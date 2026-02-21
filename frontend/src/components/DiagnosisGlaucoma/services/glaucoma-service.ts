import api from "./api";
import { GlaucomaApiResponse } from "../components/DiagnosisGlaucoma/types";

export const fetchGlaucomaDiagnosis = async (imageFile: File): Promise<GlaucomaApiResponse> => {
  const formData = new FormData();
  formData.append("image", imageFile);
  
  const response = await api.post("/diagnose-glaucoma", formData);
  return response.data;
};