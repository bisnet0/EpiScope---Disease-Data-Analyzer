import React from "react";
import { IconButton } from "@chakra-ui/react";
import { FiMessageSquare } from "react-icons/fi";

interface Props {
  onOpen: () => void;
}

export const ChatToggleButton: React.FC<Props> = ({ onOpen }) => (
  <IconButton
    icon={<FiMessageSquare size={24} />}
    colorScheme="blue"
    size="lg"
    isRound
    position="fixed"
    bottom="20px"
    right="20px"
    boxShadow="dark-lg"
    onClick={onOpen}
    aria-label="Abrir Dr. EpiScope"
    zIndex={1000}
  />
);