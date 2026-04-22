import { useColorModeValue } from '@chakra-ui/react';

export const useWomensHealthThemeFx = () => {
  // Efeito Liquid Glass padrão do seu projeto
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(26, 32, 44, 0.75)');
  const cardBorder = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  
  const innerBg = useColorModeValue('gray.50', 'rgba(0, 0, 0, 0.2)');
  const inputBg = useColorModeValue('white', 'whiteAlpha.100');
  
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.600', 'gray.400');
  
  // Cores de destaque para o módulo da mulher (ex: tons de rosa/roxo ou azul médico)
  const accentColor = useColorModeValue('pink.500', 'pink.400'); 
  const badgeBg = useColorModeValue('gray.800', 'pink.900');

  return {
    cardBg,
    cardBorder,
    innerBg,
    inputBg,
    textColor,
    mutedText,
    accentColor,
    badgeBg
  };
};