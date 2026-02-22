import { useColorModeValue } from '@chakra-ui/react';

export const useDAppThemeFx = () => {
  // Efeito Liquid Glass
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(30, 34, 45, 0.85)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  const innerBg = useColorModeValue('white', 'rgba(0, 0, 0, 0.2)');
  
  // Cores de Texto
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.600', 'gray.400');
  
  // Cores específicas da Blockchain/Tabela
  const brandColor = useColorModeValue('blue.500', 'blue.300'); // Cor do ícone Shield
  const tableHeaderBg = useColorModeValue('gray.100', 'whiteAlpha.100');
  const tableBorder = useColorModeValue('gray.200', 'whiteAlpha.100');

  return {
    cardBg,
    cardBorder,
    innerBg,
    textColor,
    mutedText,
    brandColor,
    tableHeaderBg,
    tableBorder
  };
};