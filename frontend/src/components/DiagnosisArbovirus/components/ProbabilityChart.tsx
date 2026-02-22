import { Box, Heading } from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useDiagnosisThemeFx } from '../styles/theme-fx';

export const ProbabilityChart = ({ data }: { data: any[] }) => {
  const themeFx = useDiagnosisThemeFx();

  return (
    <Box flex="1 1 400px" bg={themeFx.resultBoxBg} p={5} borderRadius="lg" border="1px solid" borderColor={themeFx.cardBorder}>
      <Heading size="sm" textAlign="center" mb={6} color={themeFx.textColor}>
        Probabilidades (Consenso)
      </Heading>
      <Box h="250px">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 10, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
            <XAxis type="number" unit="%" domain={[0, 100]} stroke={themeFx.chartTextColor} />
            <YAxis type="category" dataKey="name" width={100} stroke={themeFx.chartTextColor} />
            <Tooltip contentStyle={{ backgroundColor: themeFx.tooltipBg, borderRadius: '8px', border: 'none' }} />
            <Bar dataKey="probability" name="Confiança" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};