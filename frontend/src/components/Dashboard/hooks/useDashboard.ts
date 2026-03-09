import { useState, useEffect, useCallback } from "react";
import { fetchDashboardData } from "../services/dashboard-service";

export const useDashboard = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [periodFilter, setPeriodFilter] = useState("all");
  const [modelFilter, setModelFilter] = useState("all");

  const loadStats = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchDashboardData({ period: periodFilter, model: modelFilter });
      setStats(data);
    } catch (error) {
      console.error("Erro carregando dashboard", error);
    } finally {
      setLoading(false);
    }
  }, [periodFilter, modelFilter]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return {
    stats,
    loading,
    periodFilter,
    setPeriodFilter,
    modelFilter,
    setModelFilter,
    refresh: loadStats,
  };
};