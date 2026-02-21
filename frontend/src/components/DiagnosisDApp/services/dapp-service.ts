import api from "../../../middleware/api";
import { type HistoryItem } from "../types";

export const fetchDiagnosisHistory = async (): Promise<HistoryItem[]> => {
  const response = await api.get("/diagnose/history");
  return response.data;
};