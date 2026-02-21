import api from "./api";
import { ArbovirusApiResponse, DiagnosisPayload } from "../components/DiagnosisArbovirus/types";

export const fetchDiagnosis = async (payload: DiagnosisPayload): Promise<ArbovirusApiResponse> => {
  const response = await api.post('/diagnose', payload);
  return response.data;
};
