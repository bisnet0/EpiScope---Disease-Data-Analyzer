import React from "react";
import { useDashboard } from "./hooks/useDashboard";
import { DashboardHeader } from "./components/DashboardHeader";
import { KPICards } from "./components/Charts/KPICards";
import { StatsCharts } from "./components/Charts/StatsCharts";
import { GAAnalysisCharts } from "./components/Charts/GAAnalysisCharts";

export const DashboardPage: React.FC = () => {
  const {
    stats,
    loading,
    periodFilter,
    setPeriodFilter,
    modelFilter,
    setModelFilter,
    refresh,
  } = useDashboard();

  if (!stats && loading) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
        Carregando Centro de Comando...
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="container fade-in" style={{ paddingBottom: "50px" }}>
      <DashboardHeader
        periodFilter={periodFilter}
        setPeriodFilter={setPeriodFilter}
        modelFilter={modelFilter}
        setModelFilter={setModelFilter}
        onRefresh={refresh}
        loading={loading}
      />

      <KPICards kpis={stats.kpis} />
      
      <StatsCharts charts={stats.charts} kpis={stats.kpis} />
      
      <GAAnalysisCharts gaData={stats.charts.ga_analysis} />
    </div>
  );
};