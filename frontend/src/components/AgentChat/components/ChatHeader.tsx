import React from "react";
import { Flex, HStack, Avatar, VStack, Text, IconButton } from "@chakra-ui/react";
import { FiX } from "react-icons/fi";

interface Props {
  onClose: () => void;
}

export const ChatHeader: React.FC<Props> = ({ onClose }) => (
  <Flex bg="chat.headerBg" color="white" p={4} align="center" justify="space-between">
    <HStack>
      <Avatar size="sm" name="Dr. EpiScope" bg="blue.500" />
      <VStack align="flex-start" spacing={0}>
        <Text fontWeight="bold" fontSize="md">Dr. EpiScope</Text>
        <Text fontSize="xs" color="chat.mutedText">Agente IA Especializado</Text>
      </VStack>
    </HStack>
    <IconButton
      icon={<FiX />}
      variant="ghost"
      color="white"
      _hover={{ bg: "whiteAlpha.200" }}
      onClick={onClose}
      aria-label="Fechar"
    />
  </Flex>
);