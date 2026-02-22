import { useColorModeValue } from '@chakra-ui/react';

export const useLoginThemeFx = () => {
  // Gradiente de fundo da tela inteira
  const bgGradient = useColorModeValue(
    'linear(to-br, gray.50, blue.50)', 
    'linear(to-br, gray.900, gray.800)'
  );
  
  // Efeito Liquid Glass (Glassmorphism) para o Card
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.8)', 'rgba(26, 32, 44, 0.8)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.3)', 'rgba(255, 255, 255, 0.08)');
  
  // Cores de texto
  const textMuted = useColorModeValue('gray.600', 'gray.400');
  const linkColor = useColorModeValue('blue.500', 'blue.300');

  return {
    bgGradient,
    cardBg,
    cardBorder,
    textMuted,
    linkColor,
  };
};