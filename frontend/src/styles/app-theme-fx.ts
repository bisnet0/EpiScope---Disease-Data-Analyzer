import { useColorModeValue } from '@chakra-ui/react';

export const useAppThemeFx = () => {
  // Fundo principal
  const appBg = useColorModeValue('gray.50', '#121212');
  
  // Navbar (Liquid Glass)
  const headerBg = useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(26, 32, 44, 0.85)');
  const headerBorder = useColorModeValue('rgba(0, 0, 0, 0.05)', 'rgba(255, 255, 255, 0.08)');
  const headerShadow = useColorModeValue('sm', '0 4px 20px rgba(0, 0, 0, 0.4)');

  // Sidebar (Menu Lateral) e Footer
  const sidebarBg = useColorModeValue('white', '#1a202c');
  const footerBg = useColorModeValue('white', '#1a202c');

  // Textos
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedText = useColorModeValue('gray.500', 'gray.400');

  // Estilos dos botões de navegação lateral
  const navActiveBg = useColorModeValue('blue.50', 'rgba(100, 108, 255, 0.15)');
  const navActiveColor = useColorModeValue('blue.600', '#646cff');
  const navHoverBg = useColorModeValue('gray.100', 'whiteAlpha.100');

  return {
    appBg,
    headerBg,
    headerBorder,
    headerShadow,
    sidebarBg,
    footerBg,
    textColor,
    mutedText,
    navActiveBg,
    navActiveColor,
    navHoverBg
  };
};