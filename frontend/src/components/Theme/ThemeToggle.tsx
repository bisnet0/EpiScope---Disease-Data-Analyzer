import React from "react";
import { IconButton, useColorMode } from "@chakra-ui/react";
import { FiSun, FiMoon } from "react-icons/fi";

const ThemeToggle: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <IconButton
      aria-label="Alternar tema escuro/claro"
      icon={colorMode === "dark" ? <FiSun /> : <FiMoon />}
      onClick={toggleColorMode}
      variant="ghost"
      bg={colorMode === "dark" ? "whiteAlpha.100" : "blackAlpha.100"}
      color={colorMode === "dark" ? "yellow.400" : "blue.600"}
      fontSize="20px"
      mr={3}
      _hover={{
        bg: colorMode === "dark" ? "whiteAlpha.200" : "blackAlpha.100",
      }}
      isRound
    />
  );
};

export default ThemeToggle;
