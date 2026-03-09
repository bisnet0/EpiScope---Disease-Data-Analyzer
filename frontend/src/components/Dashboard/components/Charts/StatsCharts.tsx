import { SimpleGrid, Box, Heading, Text } from "@chakra-ui/react";
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { COLORS } from "../../utils/constants";
import { formatDateBR } from "../../utils/formatters";
import { useDashboardThemeFx } from "../../styles/theme-fx";

export const StatsCharts = ({ charts, kpis }: { charts: any; kpis: any }) => {
  const themeFx = useDashboardThemeFx();

  const diagnosisData = [
    { name: "Arboviroses", value: kpis.arbovirus_count },
    { name: "Glaucoma", value: kpis.glaucoma_count },
  ];

  const learningCurveData = charts.learning_curve.map((item: any) => ({
    ...item,
    dateLabel: formatDateBR(item.date),
  }));

  const GlassCard = ({ children, title }: any) => (
    <Box bg={themeFx.cardBg} p={6} borderRadius="xl" border="1px solid" borderColor={themeFx.cardBorder} boxShadow="lg" backdropFilter="blur(16px)">
      <Heading size="sm" mb={5} pb={3} borderBottom="1px solid" borderColor={themeFx.cardBorder} color={themeFx.textColor}>
        {title}
      </Heading>
      {children}
    </Box>
  );

  return (
    <>
      <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={6} mb={6}>
        {/* Evolução */}
        <GlassCard title="📈 Evolução da Inteligência Artificial">
          <Box h="300px">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={learningCurveData}>
                <defs>
                  <linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={themeFx.accentColor} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={themeFx.accentColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
                <XAxis dataKey="dateLabel" stroke={themeFx.chartTextColor} fontSize={12} />
                <YAxis domain={[50, 100]} stroke={themeFx.chartTextColor} unit="%" fontSize={12} />
                <Tooltip contentStyle={{ background: themeFx.tooltipBg, border: `1px solid ${themeFx.tooltipBorder}`, borderRadius: "8px" }} />
                <Area type="monotone" dataKey="accuracy" name="Acurácia" stroke={themeFx.accentColor} strokeWidth={3} fillOpacity={1} fill="url(#colorAcc)" />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
          <Text fontSize="xs" color={themeFx.mutedText} textAlign="center" mt={3}>Mostrando treinos dos filtros selecionados.</Text>
        </GlassCard>

        {/* Performance Algoritmos */}
        <GlassCard title="⚔️ Performance Média por Algoritmo">
          <Box h="300px">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.model_performance} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
                <XAxis type="number" domain={[0, 100]} stroke={themeFx.chartTextColor} unit="%" />
                <YAxis type="category" dataKey="name" width={100} stroke={themeFx.chartTextColor} fontSize={12} />
                <Tooltip contentStyle={{ background: themeFx.tooltipBg, border: `1px solid ${themeFx.tooltipBorder}`, borderRadius: "8px" }} cursor={{ fill: "rgba(100,100,100,0.1)" }} />
                <Bar dataKey="accuracy" name="Acurácia Média" barSize={25} radius={[0, 4, 4, 0]}>
                  {charts.model_performance.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </GlassCard>
      </SimpleGrid>

      {/* Distribuição */}
      <SimpleGrid columns={1} mb={6}>
        <GlassCard title="📊 Distribuição de Patologias">
          <Box h="250px" display="flex" alignItems="center" justifyContent="center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={diagnosisData} cx="50%" cy="50%" innerRadius={70} outerRadius={90} paddingAngle={5} dataKey="value" stroke="none">
                  <Cell fill="#3498db" />
                  <Cell fill="#e91e63" />
                </Pie>
                <Tooltip contentStyle={{ background: themeFx.tooltipBg, border: `1px solid ${themeFx.tooltipBorder}`, borderRadius: "8px" }} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </GlassCard>
      </SimpleGrid>
    </>
  );
};