import { useColorModeValue } from '@chakra-ui/react';

export const useChatThemeFx = () => {
  // Efeito Liquid Glass do Container Principal
  const containerBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(22, 28, 36, 0.85)');
  const borderColor = useColorModeValue('rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.08)');
  
  // Cabeçalho e Rodapé
  const headerBg = useColorModeValue('blue.500', 'rgba(0, 0, 0, 0.4)');
  const headerText = 'white';
  const inputAreaBg = useColorModeValue('whiteAlpha.800', 'rgba(0, 0, 0, 0.2)');
  const inputBg = useColorModeValue('gray.100', 'whiteAlpha.100');

  // Bolhas de Mensagem
  const userMsgBg = useColorModeValue('blue.500', 'blue.400');
  const userMsgText = 'white';
  const agentMsgBg = useColorModeValue('gray.100', 'rgba(255, 255, 255, 0.05)');
  const agentMsgText = useColorModeValue('gray.800', 'whiteAlpha.900');

  // Textos e Ícones
  const mutedText = useColorModeValue('gray.500', 'gray.400');
  const iconColor = useColorModeValue('blue.500', 'blue.300');

  return {
    containerBg,
    borderColor,
    headerBg,
    headerText,
    inputAreaBg,
    inputBg,
    userMsgBg,
    userMsgText,
    agentMsgBg,
    agentMsgText,
    mutedText,
    iconColor
  };
};