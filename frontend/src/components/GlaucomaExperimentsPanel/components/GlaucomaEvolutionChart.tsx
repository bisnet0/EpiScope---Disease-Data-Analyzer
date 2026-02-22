import React from 'react';
import { Box, Heading, Center, Text } from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { type GlaucomaEvolutionChartProps } from '../types';
import { useGlaucomaExpThemeFx } from '../styles/theme-fx';


export const GlaucomaEvolutionChart: React.FC<GlaucomaEvolutionChartProps> = ({ history, modelType }) => {
  const themeFx = useGlaucomaExpThemeFx();

  return (
    <Box 
      flex="2 1 400px" 
      bg={themeFx.cardBg} 
      p={6} 
      borderRadius="xl" 
      minH="350px"
      border="1px solid" 
      borderColor={themeFx.cardBorder}
      backdropFilter="blur(16px)"
      boxShadow="lg"
    >
      {history.length > 0 ? (
        <Box w="full" h="300px">
          <Heading size="sm" textAlign="center" mb={6} color={themeFx.textColor}>
            Evolução da Acurácia (CNN + {modelType.toUpperCase()})
          </Heading>
          <ResponsiveContainer>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
              <XAxis dataKey="generation" label={{ value: 'Geração', position: 'insideBottom', offset: -5, fill: themeFx.chartTextColor }} stroke={themeFx.chartTextColor} />
              <YAxis domain={['auto', 'auto']} unit="%" stroke={themeFx.chartTextColor} />
              <Tooltip contentStyle={{ backgroundColor: themeFx.tooltipBg, borderRadius: '8px', border: 'none' }} />
              <Legend verticalAlign="top" height={36} />
              <Line type="monotone" dataKey="best_accuracy" name="Melhor Config" stroke="#e91e63" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="avg_accuracy" name="Média População" stroke="#8884d8" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      ) : (
        <Center h="100%" flexDirection="column" color={themeFx.mutedText}>
          <Text>O gráfico de evolução aparecerá aqui.</Text>
        </Center>
      )}
    </Box>
  );
};