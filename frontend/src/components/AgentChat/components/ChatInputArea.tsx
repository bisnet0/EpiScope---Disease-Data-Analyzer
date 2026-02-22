import React from "react";
import { Flex, Input, IconButton } from "@chakra-ui/react";
import { FiPaperclip, FiSend } from "react-icons/fi";
import { useChatThemeFx } from "../styles/theme-fx";
import { type ChatInputAreaProps } from "../types";


export const ChatInputArea: React.FC<ChatInputAreaProps> = ({
  inputValue, attachment, isLoading, onInputChange, onFileChange, onSendMessage, onKeyPress
}) => {
  const themeFx = useChatThemeFx();

  return (
    <Flex 
      p={4} 
      bg={themeFx.inputAreaBg} 
      borderTop="1px solid" 
      borderColor={themeFx.borderColor} 
      align="center"
    >
      <input type="file" id="file-upload" style={{ display: "none" }} onChange={onFileChange} accept="image/*" />
      <IconButton
        as="label"
        htmlFor="file-upload"
        icon={<FiPaperclip />}
        variant="ghost"
        color={attachment ? themeFx.iconColor : themeFx.mutedText}
        mr={2}
        aria-label="Anexar arquivo"
        cursor="pointer"
        _hover={{ bg: "whiteAlpha.200" }}
      />
      <Input
        flex={1}
        placeholder="Descreva os sintomas ou envie arquivo..."
        color={themeFx.agentMsgText}
        value={inputValue}
        onChange={(e) => onInputChange(e.target.value)}
        onKeyDown={onKeyPress}
        variant="filled"
        bg={themeFx.inputBg}
        _hover={{ bg: themeFx.inputBg }}
        _focus={{ bg: themeFx.inputBg, borderColor: themeFx.iconColor }}
        borderRadius="full"
      />
      <IconButton
        icon={<FiSend />}
        colorScheme="blue"
        isRound
        ml={2}
        onClick={onSendMessage}
        isLoading={isLoading}
        aria-label="Enviar"
      />
    </Flex>
  );
};