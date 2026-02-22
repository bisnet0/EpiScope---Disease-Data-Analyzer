import React from "react";
import { Box, Heading } from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import { type GlaucomaResultChartProps } from "../types";
import { formatResponseHtml } from "../utils/formatters";
import { useGlaucomaThemeFx } from '../styles/theme-fx';



export const GlaucomaResultChart: React.FC<GlaucomaResultChartProps> = ({ result, chartData }) => {
  const themeFx = useGlaucomaThemeFx();

  return (
    <Box 
      bg={themeFx.cardBg} 
      p={{ base: 5, md: 8 }} 
      borderRadius="xl" 
      border="1px solid" 
      borderColor={themeFx.cardBorder} 
      backdropFilter="blur(16px)" 
      boxShadow="lg"
    >
      <Heading size="md" mb={4} color={themeFx.textColor}>
        👁️ Resultado da Visão Computacional
      </Heading>
      
      <Box 
        color={themeFx.textColor}
        mb={8}
        dangerouslySetInnerHTML={{ __html: formatResponseHtml(result.friendly_response) }} 
        sx={{
          'strong': { color: 'pink.500' },
          'br': { mb: 2 }
        }}
      />

      <Box h="250px" mt={6} bg={themeFx.resultBoxBg} p={4} borderRadius="lg" border="1px solid" borderColor={themeFx.cardBorder}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={themeFx.chartGridColor} />
            <XAxis type="number" unit="%" domain={[0, 100]} stroke={themeFx.chartTextColor} />
            <YAxis type="category" dataKey="name" width={100} stroke={themeFx.chartTextColor} />
            <Tooltip contentStyle={{ backgroundColor: themeFx.tooltipBg, borderRadius: '8px', border: 'none' }} />
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            <Bar dataKey="probability" name="Confiança (%)" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};