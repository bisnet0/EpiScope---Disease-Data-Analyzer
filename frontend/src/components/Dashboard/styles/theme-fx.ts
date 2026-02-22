import { useColorModeValue } from '@chakra-ui/react';

export const useDashboardThemeFx = () => {
  // Efeito Liquid Glass para os Cards
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(30, 34, 45, 0.85)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  
  // Elementos Internos e Filtros
  const filterPanelBg = useColorModeValue('white', 'rgba(0, 0, 0, 0.2)');
  const inputBg = useColorModeValue('gray.50', 'whiteAlpha.100');
  
  // Textos
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.600', 'gray.400');
  const accentColor = useColorModeValue('blue.500', '#646cff');

  // Cores do Recharts (adaptativas para Dark/Light mode)
  const chartGridColor = useColorModeValue('#e2e8f0', '#333');
  const chartTextColor = useColorModeValue('#4a5568', '#aaa');
  const tooltipBg = useColorModeValue('#ffffff', '#252525');
  const tooltipBorder = useColorModeValue('#e2e8f0', '#444');

  return {
    cardBg,
    cardBorder,
    filterPanelBg,
    inputBg,
    textColor,
    mutedText,
    accentColor,
    chartGridColor,
    chartTextColor,
    tooltipBg,
    tooltipBorder
  };
};