import api from "../../../middleware/api";
import { type ArbovirusApiResponse, type DiagnosisPayload } from "../types";

export const fetchDiagnosis = async (payload: DiagnosisPayload): Promise<ArbovirusApiResponse> => {
  const response = await api.post('/arbovirus/diagnose', payload);
  return response.data;
};
