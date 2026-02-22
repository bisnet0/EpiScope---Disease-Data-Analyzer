import { useColorModeValue } from '@chakra-ui/react';

export const useExperimentsThemeFx = () => {
  // Efeito Liquid Glass para os cards
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(30, 34, 45, 0.85)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  
  // Fundos internos (como a área de config avançada)
  const innerBg = useColorModeValue('gray.50', 'rgba(0, 0, 0, 0.2)');
  const inputBg = useColorModeValue('white', 'whiteAlpha.100');
  
  // Textos e Destaques
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.600', 'gray.400');
  const accentColor = useColorModeValue('purple.500', 'purple.300'); // Cor da Evolução
  const successColor = useColorModeValue('green.500', 'green.300');  // Cor do Manual

  // Cores do Recharts adaptativas
  const chartGridColor = useColorModeValue('#e2e8f0', '#444');
  const chartTextColor = useColorModeValue('#4a5568', '#aaa');
  const tooltipBg = useColorModeValue('#ffffff', '#252525');

  return {
    cardBg,
    cardBorder,
    innerBg,
    inputBg,
    textColor,
    mutedText,
    accentColor,
    successColor,
    chartGridColor,
    chartTextColor,
    tooltipBg
  };
};