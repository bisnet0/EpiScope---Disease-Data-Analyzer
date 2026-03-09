import React from 'react';
import { Box, Heading, Text } from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { MODEL_COLORS } from '../utils/constants';
import { useDiagnosisThemeFx } from '../styles/theme-fx';
import { type AlgorithmsChartProps } from '../types';



export const AlgorithmsChart: React.FC<AlgorithmsChartProps> = ({ data, winnerModel }) => {
  const themeFx = useDiagnosisThemeFx();

  if (data.length === 0) return null;

  return (
    <Box flex="1 1 400px" bg={themeFx.resultBoxBg} p={5} borderRadius="lg" border="1px solid" borderColor={themeFx.cardBorder}>
      <Heading size="sm" textAlign="center" mb={6} color={themeFx.textColor}>
        Comparativo de Algoritmos
      </Heading>
      <Box h="250px">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
            <XAxis dataKey="name" stroke={themeFx.chartTextColor} fontSize={10} tickFormatter={(v) => v.split(' ')[0]} />
            <YAxis unit="%" domain={[0, 100]} stroke={themeFx.chartTextColor} />
            <Tooltip contentStyle={{ backgroundColor: themeFx.tooltipBg, borderRadius: '8px', border: 'none' }} />
            <ReferenceLine y={50} stroke={themeFx.mutedText} strokeDasharray="3 3" />
            <Bar dataKey="confidence" name="Certeza" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-md-${index}`} fill={MODEL_COLORS[entry.key] || '#888'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
      {winnerModel && (
        <Text textAlign="center" fontSize="sm" color={themeFx.mutedText} mt={4}>
          Vencedor: <Text as="span" fontWeight="bold" color={themeFx.textColor}>{winnerModel.toUpperCase().replace('_', ' ')}</Text>
        </Text>
      )}
    </Box>
  );
};