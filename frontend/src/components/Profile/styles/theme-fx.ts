import { useColorModeValue } from '@chakra-ui/react';

export const useToastThemeFx = () => {
  // --- LIQUID GLASS ADAPTATIVO ---
  // Dark: Quase preto/azul navy. Light: Branco translúcido
  const cardBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(22, 28, 36, 0.85)');
  const cardBorder = useColorModeValue('rgba(0, 0, 0, 0.05)', 'rgba(255, 255, 255, 0.08)');
  const cardShadow = useColorModeValue(
    '0 20px 40px -4px rgba(0, 0, 0, 0.1)', 
    '0 20px 40px -4px rgba(0, 0, 0, 0.4)'
  );

  // Cores de texto
  const titleColor = useColorModeValue('gray.800', '#FFFFFF');
  const messageColor = useColorModeValue('gray.600', '#919EAB');

  // Cores do botão de fechar
  const closeIconColor = useColorModeValue('gray.400', '#637381');
  const closeIconHoverBg = useColorModeValue('blackAlpha.100', 'whiteAlpha.200');
  const closeIconHoverColor = useColorModeValue('black', 'white');

  return {
    cardBg,
    cardBorder,
    cardShadow,
    titleColor,
    messageColor,
    closeIconColor,
    closeIconHoverBg,
    closeIconHoverColor
  };
};