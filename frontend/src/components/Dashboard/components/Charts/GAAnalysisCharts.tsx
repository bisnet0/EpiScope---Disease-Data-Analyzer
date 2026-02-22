import { SimpleGrid, Box, Heading, Text } from "@chakra-ui/react";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useDashboardThemeFx } from "../../styles/theme-fx";

export const GAAnalysisCharts = ({ gaData }: { gaData: any }) => {
  const themeFx = useDashboardThemeFx();

  if (!gaData || !gaData.mutation || gaData.mutation.length === 0) return null;

  const GlassChartCard = ({ title, children, desc }: any) => (
    <Box bg={themeFx.cardBg} p={5} borderRadius="xl" border="1px solid" borderColor={themeFx.cardBorder} boxShadow="md" backdropFilter="blur(16px)">
      <Heading size="xs" color={themeFx.mutedText} mb={4} textTransform="uppercase">{title}</Heading>
      <Box h="200px">{children}</Box>
      <Text fontSize="xs" color={themeFx.mutedText} mt={3} textAlign="center">{desc}</Text>
    </Box>
  );

  return (
    <Box mt={10} pt={8} borderTop="1px solid" borderColor={themeFx.cardBorder}>
      <Heading size="md" mb={6} display="flex" alignItems="center" gap={3} color={themeFx.textColor}>
        🧬 Teoria Evolutiva: Análise de Hiperparâmetros
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 3 }} spacing={6}>
        
        <GlassChartCard title="⚡ Taxa de Mutação vs Acurácia" desc="Impacto da aleatoriedade.">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={gaData.mutation}>
              <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
              <XAxis dataKey="x" type="number" domain={[0, "dataMax"]} stroke={themeFx.chartTextColor} fontSize={10} tickFormatter={v => `${v * 100}%`} />
              <YAxis domain={["auto", "auto"]} hide />
              <Tooltip contentStyle={{ background: themeFx.tooltipBg, borderRadius: "8px", border: "none" }} formatter={(val: number) => `${val}%`} labelFormatter={l => `Mutação: ${l * 100}%`} />
              <Line type="monotone" dataKey="y" stroke="#FF8042" dot={{ r: 3 }} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </GlassChartCard>

        <GlassChartCard title="👥 Tamanho da População" desc="Populações maiores garantem diversidade?">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={gaData.population}>
              <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
              <XAxis dataKey="x" stroke={themeFx.chartTextColor} fontSize={10} />
              <YAxis domain={[0, 100]} hide />
              <Tooltip contentStyle={{ background: themeFx.tooltipBg, borderRadius: "8px", border: "none" }} cursor={{ fill: "transparent" }} />
              <Bar dataKey="y" fill="#00C49F" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassChartCard>

        <GlassChartCard title="🧬 Taxa de Crossover" desc="Impacto de misturar genes de pais diferentes.">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={gaData.crossover}>
              <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
              <XAxis dataKey="x" stroke={themeFx.chartTextColor} fontSize={10} tickFormatter={v => `${v * 100}%`} />
              <YAxis domain={["auto", "auto"]} hide />
              <Tooltip contentStyle={{ background: themeFx.tooltipBg, borderRadius: "8px", border: "none" }} labelFormatter={l => `Crossover: ${l * 100}%`} />
              <Area type="monotone" dataKey="y" stroke="#8884d8" fill="#8884d8" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </GlassChartCard>

      </SimpleGrid>
    </Box>
  );
};