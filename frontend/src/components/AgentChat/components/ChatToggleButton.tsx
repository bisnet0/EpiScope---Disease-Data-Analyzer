import React from "react";
import { IconButton } from "@chakra-ui/react";
import { FiMessageSquare } from "react-icons/fi";
import { type ChatToggleButtonProps } from "../types";


export const ChatToggleButton: React.FC<ChatToggleButtonProps> = ({ onOpen }) => (
  <IconButton
    icon={<FiMessageSquare size={24} />}
    colorScheme="blue"
    size="lg"
    isRound
    position="fixed"
    bottom="20px"
    right={{ base: "10px", md: "20px" }}
    boxShadow="0 4px 12px rgba(0, 0, 0, 0.3)"
    onClick={onOpen}
    aria-label="Abrir Dr. EpiScope"
    zIndex={1000}
    _hover={{ transform: 'scale(1.05)' }}
    transition="all 0.2s"
  />
);