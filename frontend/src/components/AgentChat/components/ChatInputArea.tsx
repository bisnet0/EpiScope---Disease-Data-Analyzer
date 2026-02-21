import React, { ChangeEvent, KeyboardEvent } from "react";
import { Flex, Input, IconButton } from "@chakra-ui/react";
import { FiPaperclip, FiSend } from "react-icons/fi";

interface Props {
  inputValue: string;
  attachment: string | null;
  isLoading: boolean;
  onInputChange: (val: string) => void;
  onFileChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onSendMessage: () => void;
  onKeyPress: (e: KeyboardEvent<HTMLInputElement>) => void;
}

export const ChatInputArea: React.FC<Props> = ({
  inputValue, attachment, isLoading, onInputChange, onFileChange, onSendMessage, onKeyPress
}) => (
  <Flex p={4} bg="chat.inputAreaBg" borderTop="1px solid" borderColor="chat.borderColor" align="center">
    <input type="file" id="file-upload" style={{ display: "none" }} onChange={onFileChange} accept="image/*" />
    <IconButton
      as="label"
      htmlFor="file-upload"
      icon={<FiPaperclip />}
      variant="ghost"
      color={attachment ? "blue.500" : "gray.500"}
      mr={2}
      aria-label="Anexar arquivo"
      cursor="pointer"
    />
    <Input
      flex={1}
      placeholder="Descreva os sintomas ou envie um arquivo..."
      textColor="chat.mutedText"
      value={inputValue}
      onChange={(e) => onInputChange(e.target.value)}
      onKeyDown={onKeyPress}
      variant="filled"
      bg="chat.inputBg"
      _focus={{ bg: "chat.inputBg", borderColor: "blue.400" }}
    />
    <IconButton
      icon={<FiSend />}
      colorScheme="blue"
      ml={2}
      onClick={onSendMessage}
      isLoading={isLoading}
      aria-label="Enviar"
    />
  </Flex>
);