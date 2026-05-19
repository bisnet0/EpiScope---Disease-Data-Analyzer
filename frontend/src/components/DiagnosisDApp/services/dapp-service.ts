import api from "../../../middleware/api";
import { type HistoryItem } from "../types";

export const fetchDiagnosisHistory = async (): Promise<HistoryItem[]> => {
  const response = await api.get("patients/diagnose/history");
  return response.data;
};