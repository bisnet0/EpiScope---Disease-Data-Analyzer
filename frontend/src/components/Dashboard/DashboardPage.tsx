import React from "react";
import { Box, Text, Center, Spinner } from "@chakra-ui/react";
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
      <Center h="50vh" flexDirection="column" gap={4}>
        <Spinner size="xl" color="blue.500" thickness="4px" />
        <Text color="gray.500" fontWeight="medium">Inicializando Centro de Comando...</Text>
      </Center>
    );
  }

  if (!stats) return null;

  return (
    <Box w="full" maxW="1400px" mx="auto" pb={10} animation="fade-in 0.4s">
      
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

    </Box>
  );
};