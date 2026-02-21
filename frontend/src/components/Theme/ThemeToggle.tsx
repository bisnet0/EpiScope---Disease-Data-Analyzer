import React from 'react';
import { IconButton, useColorMode } from '@chakra-ui/react';
import { FiSun, FiMoon } from 'react-icons/fi';

const ThemeToggle: React.FC = () => {
  // Esse hook mágico puxa o modo atual ('light' ou 'dark') e a função que inverte ele
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <IconButton
      aria-label="Alternar tema escuro/claro"
      icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
      onClick={toggleColorMode}
      variant="ghost"
      // Se for escuro, mostra o sol amarelinho. Se for claro, mostra a lua azulada.
      color={colorMode === 'dark' ? 'yellow.400' : 'blue.600'}
      fontSize="20px"
      mr={3} // Uma margem para não ficar colado nos outros itens do Header
      _hover={{ bg: colorMode === 'dark' ? 'whiteAlpha.200' : 'blackAlpha.100' }}
      isRound
    />
  );
};

export default ThemeToggle;