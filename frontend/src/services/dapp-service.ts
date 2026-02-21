import api from "./api";
import { HistoryItem } from "../components/DiagnosisDApp/types";

export const fetchDiagnosisHistory = async (): Promise<HistoryItem[]> => {
  const response = await api.get("/diagnose/history");
  return response.data;
};