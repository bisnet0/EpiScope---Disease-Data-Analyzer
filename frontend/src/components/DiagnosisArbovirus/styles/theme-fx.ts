import { useColorModeValue } from '@chakra-ui/react';

export const useDiagnosisThemeFx = () => {
  // Efeito Liquid Glass para os cards principais
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(30, 34, 45, 0.85)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  const mosquitoBg = useColorModeValue('#099d13', '#0d832c'); // Roxo translúcido para o ícone do mosquito
  
  // Fundos para inputs e áreas de destaque (como os gráficos)
  const inputBg = useColorModeValue('white', 'whiteAlpha.100');
  const resultBoxBg = useColorModeValue('gray.50', 'whiteAlpha.50');
  
  // Cores de texto
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.600', 'gray.400');
  const brandColor = useColorModeValue('green.500', 'green.300'); // Para o botão do lab

  // Cores dinâmicas para o Recharts
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
    brandColor,
    chartGridColor,
    chartTextColor,
    tooltipBg,
    mosquitoBg
  };
};