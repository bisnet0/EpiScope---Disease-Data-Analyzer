import api from "../../../middleware/api";
import { type GlaucomaApiResponse } from "../types";

export const fetchGlaucomaDiagnosis = async (imageFile: File): Promise<GlaucomaApiResponse> => {
  const formData = new FormData();
  formData.append("image", imageFile);
  
  const response = await api.post("/glaucoma/diagnose-glaucoma", formData);
  return response.data;
};