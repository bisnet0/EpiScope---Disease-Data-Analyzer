import { useColorModeValue } from "@chakra-ui/react";

export const useLoginThemeFx = () => {
  const cardBg = useColorModeValue(
    "rgba(255, 255, 255, 0.8)",
    "rgba(26, 32, 44, 0.8)",
  );
  const cardBorder = useColorModeValue(
    "rgba(255, 255, 255, 0.3)",
    "rgba(255, 255, 255, 0.08)",
  );

  const textColor = useColorModeValue("gray.800", "white");
  const textMuted = useColorModeValue("gray.600", "gray.400");
  const linkColor = useColorModeValue("blue.500", "blue.300");

  return {
    cardBg,
    cardBorder,
    textColor,
    textMuted,
    linkColor,
  };
};
