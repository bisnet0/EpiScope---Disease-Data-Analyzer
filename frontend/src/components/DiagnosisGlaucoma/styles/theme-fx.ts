import { useColorModeValue } from '@chakra-ui/react';

export const useGlaucomaThemeFx = () => {
  // Efeito Liquid Glass para os cards
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(30, 34, 45, 0.85)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  
  // Elementos internos
  const inputBg = useColorModeValue('white', 'whiteAlpha.100');
  const resultBoxBg = useColorModeValue('gray.50', 'whiteAlpha.50');
  
  // Cores de texto
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.600', 'gray.400');

  // Cores do Recharts (adaptativas para Dark/Light mode)
  const chartGridColor = useColorModeValue('#e2e8f0', '#444');
  const chartTextColor = useColorModeValue('#4a5568', '#aaa');
  const tooltipBg = useColorModeValue('#ffffff', '#252525');

  return {
    cardBg,
    cardBorder,
    inputBg,
    resultBoxBg,
    textColor,
    mutedText,
    chartGridColor,
    chartTextColor,
    tooltipBg
  };
};