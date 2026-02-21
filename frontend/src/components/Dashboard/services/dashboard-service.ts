import api from "../../../middleware/api";

export interface DashboardFilters {
  period: string;
  model: string;
}

export const fetchDashboardData = async (params: DashboardFilters) => {
  const response = await api.get("/dashboard/stats", { params });
  return response.data;
};