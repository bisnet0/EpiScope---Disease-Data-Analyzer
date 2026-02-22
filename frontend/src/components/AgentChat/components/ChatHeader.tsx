import React from "react";
import { Flex, HStack, Avatar, VStack, Text, IconButton } from "@chakra-ui/react";
import { FiX } from "react-icons/fi";
import { useChatThemeFx } from "../styles/theme-fx";
import { type ChatHeaderProps } from "../types";


export const ChatHeader: React.FC<ChatHeaderProps> = ({ onClose }) => {
  const themeFx = useChatThemeFx();

  return (
    <Flex 
      bg={themeFx.headerBg} 
      color={themeFx.headerText} 
      p={4} 
      align="center" 
      justify="space-between"
      borderBottom="1px solid"
      borderColor={themeFx.borderColor}
    >
      <HStack>
        <Avatar size="sm" name="Dr. EpiScope" bg="blue.600" color="white" />
        <VStack align="flex-start" spacing={0}>
          <Text fontWeight="bold" fontSize="md">Dr. EpiScope</Text>
          <Text fontSize="xs" color="whiteAlpha.800">Agente IA Especializado</Text>
        </VStack>
      </HStack>
      <IconButton
        icon={<FiX size={20} />}
        variant="ghost"
        color={themeFx.headerText}
        _hover={{ bg: "whiteAlpha.200" }}
        onClick={onClose}
        aria-label="Fechar"
        size="sm"
      />
    </Flex>
  );
};