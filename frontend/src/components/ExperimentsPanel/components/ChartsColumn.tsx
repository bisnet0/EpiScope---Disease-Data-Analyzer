import React from 'react';
import { Box, Button, Flex, Text, Center } from '@chakra-ui/react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine, Legend } from 'recharts';
import { type ChartsColumnProps } from '../types';
import { useExperimentsThemeFx } from '../styles/theme-fx';


export const ChartsColumn: React.FC<ChartsColumnProps> = ({ viewMode, setViewMode, manualHistory, evolutionHistory }) => {
  const themeFx = useExperimentsThemeFx();

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
      
      {/* Toggle de Visualização */}
      <Flex mb={6} borderBottom="1px solid" borderColor={themeFx.cardBorder} pb={4} gap={4}>
        <Button 
          variant={viewMode === 'manual' ? 'solid' : 'ghost'} 
          colorScheme={viewMode === 'manual' ? 'green' : 'gray'}
          onClick={() => setViewMode('manual')} 
        >
          📊 Histórico Manual
        </Button>
        <Button 
          variant={viewMode === 'evolution' ? 'solid' : 'ghost'} 
          colorScheme={viewMode === 'evolution' ? 'purple' : 'gray'}
          onClick={() => setViewMode('evolution')} 
        >
          🧬 Linha do Tempo Evolutiva
        </Button>
      </Flex>

      {/* GRÁFICO MANUAL (BARRAS) */}
      {viewMode === 'manual' && manualHistory.length > 0 && (
        <Box w="full" h="280px">
          <ResponsiveContainer>
            <BarChart data={manualHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
              <XAxis dataKey="name" stroke={themeFx.chartTextColor} fontSize={12} />
              <YAxis domain={[0, 100]} unit="%" stroke={themeFx.chartTextColor} />
              <Tooltip contentStyle={{ backgroundColor: themeFx.tooltipBg, borderRadius: '8px', border: 'none' }} />
              <ReferenceLine y={70} label={{ position: 'top', value: 'Meta (70%)', fill: 'red' }} stroke="red" strokeDasharray="3 3" />
              <Bar dataKey="accuracy" name="Acurácia" radius={[4, 4, 0, 0]}>
                {manualHistory.map((e, i) => (
                  <Cell key={i} fill={e.model === 'xgboost' ? '#3498db' : '#2ecc71'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}

      {/* GRÁFICO EVOLUTIVO (LINHAS) */}
      {viewMode === 'evolution' && evolutionHistory.length > 0 ? (
        <Box w="full" h="280px">
          <ResponsiveContainer>
            <LineChart data={evolutionHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
              <XAxis dataKey="generation" label={{ value: 'Geração', position: 'insideBottom', offset: -5, fill: themeFx.chartTextColor }} stroke={themeFx.chartTextColor} />
              <YAxis domain={['auto', 'auto']} unit="%" stroke={themeFx.chartTextColor} />
              <Tooltip contentStyle={{ backgroundColor: themeFx.tooltipBg, borderRadius: '8px', border: 'none' }} />
              <Legend verticalAlign="top" height={36} />
              <Line type="monotone" dataKey="best_accuracy" name="Melhor Indivíduo" stroke="#8e44ad" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="avg_accuracy" name="Média da População" stroke="#8884d8" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
          <Text textAlign="center" fontSize="sm" color={themeFx.mutedText} mt={4}>
            O algoritmo seleciona os melhores modelos e cria "filhos" (Crossover/Mutação) a cada geração.
          </Text>
        </Box>
      ) : (
        viewMode === 'evolution' && (
          <Center h="200px" flexDirection="column" color={themeFx.mutedText}>
            <Text>Nenhuma evolução rodada ainda.</Text>
            <Text fontSize="sm">Clique em "🧬 Evoluir" para iniciar a seleção natural.</Text>
          </Center>
        )
      )}

      {/* STATUS VAZIO (MANUAL) */}
      {viewMode === 'manual' && manualHistory.length === 0 && (
        <Center h="200px" color={themeFx.mutedText}>
          <Text>Configure os parâmetros e rode um teste.</Text>
        </Center>
      )}
    </Box>
  );
};