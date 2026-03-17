import api from "../../../middleware/api";

export const fetchXRayDiagnosis = async (imageFile: File) => {
  const formData = new FormData();
  formData.append("image", imageFile);
  
  const response = await api.post("/diagnose-xray", formData);
  return response.data;
};