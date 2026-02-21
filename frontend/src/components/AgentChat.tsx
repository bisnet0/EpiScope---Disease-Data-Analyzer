import React, { useState, useEffect, useRef } from "react";
import type { ChangeEvent, KeyboardEvent } from "react";
import {
  Flex,
  Box,
  Input,
  IconButton,
  Text,
  VStack,
  HStack,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
  Spinner,
} from "@chakra-ui/react";
import {
  FiSend,
  FiPaperclip,
  FiMoreVertical,
  FiMessageSquare,
  FiX,
  FiTrash2,
} from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import api from "../middleware/api";

interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  has_attachment?: boolean;
  created_at?: string;
}

interface ChatResponse {
  response: string;
  msg_id: string;
  status: string;
}

const AgentChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const [attachment, setAttachment] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const toast = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    try {
      const response = await api.get<Message[]>("/agent/history");
      setMessages(response.data);
    } catch (error) {
      console.error("Erro ao carregar histórico", error);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachment(reader.result as string);
        toast({
          title: "Arquivo anexado",
          description: file.name,
          status: "success",
          duration: 2000,
          isClosable: true,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && !attachment) return;

    const newMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      has_attachment: !!attachment,
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputValue("");
    setIsLoading(true);

    const payload = {
      message: newMsg.content,
      attachment: attachment,
    };

    setAttachment(null);

    try {
      const response = await api.post<ChatResponse>("/agent/chat", payload);
      const agentMsg: Message = {
        id: response.data.msg_id,
        role: "agent",
        content: response.data.response,
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (error) {
      toast({
        title: "Erro de comunicação",
        description: "O Dr. EpiScope está indisponível.",
        status: "error",
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  const handleSoftDelete = (msgId: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== msgId));
    toast({
      title: "Mensagem ocultada",
      description: "Ela ainda está salva no histórico do sistema.",
      status: "info",
      duration: 3000,
    });
  };

  if (!isOpen) {
    return (
      <IconButton
        icon={<FiMessageSquare size={24} />}
        colorScheme="blue"
        size="lg"
        isRound
        position="fixed"
        bottom="20px"
        right="20px"
        boxShadow="dark-lg"
        onClick={() => setIsOpen(true)}
        aria-label="Abrir Dr. EpiScope"
        zIndex={1000}
      />
    );
  }

  return (
    <Box
      position="fixed"
      bottom="20px"
      right={{ base: "10px", md: "20px" }}
      zIndex={1000}
    >
      <Flex
        w={{ base: "calc(100vw - 65px)", md: "600px", lg: "800px" }}
        ml={{ base: "0", md: "0.5%" }}
        height={{ base: "calc(100vh - 200px)", md: "calc(100vh - 150px)" }}
        flexDirection="column"
        mx="auto"
        borderRadius="8px"
        bg="chat.containerBg"
        boxShadow="rgba(0, 0, 0, 0.16) 0px 1px 4px, rgba(0, 0, 0, 0.2) 0px 10px 20px"
        overflow="hidden"
        border="1px solid"
        borderColor="chat.borderColor"
        backdropFilter="blur(10px)"
      >
        <Flex
          bg="chat.headerBg"
          color="white"
          p={4}
          align="center"
          justify="space-between"
        >
          <HStack>
            <Avatar size="sm" name="Dr. EpiScope" bg="blue.500" />
            <VStack align="flex-start" spacing={0}>
              <Text fontWeight="bold" fontSize="md">
                Dr. EpiScope
              </Text>
              <Text fontSize="xs" color="chat.mutedText">
                Agente IA Especializado
              </Text>
            </VStack>
          </HStack>
          <IconButton
            icon={<FiX />}
            variant="ghost"
            color="white"
            _hover={{ bg: "whiteAlpha.200" }}
            onClick={() => setIsOpen(false)}
            aria-label="Fechar"
          />
        </Flex>

        <Flex
          flex={1}
          direction="column"
          p={4}
          overflowY="auto"
          bg="chat.areaBg"
        >
          {messages.map((msg) => (
            <Flex
              key={msg.id}
              justify={msg.role === "user" ? "flex-end" : "flex-start"}
              mb={4}
            >
              <Flex
                maxW="80%"
                bg={msg.role === "user" ? "blue.500" : "chat.agentMsgBg"}
                color={msg.role === "user" ? "white" : "chat.agentMsgText"}
                p={3}
                borderRadius="lg"
                boxShadow="sm"
                border={msg.role === "agent" ? "1px solid" : "none"}
                borderColor={
                  msg.role === "agent" ? "chat.borderColor" : "transparent"
                }
                position="relative"
                role="group"
              >
                <Box
                  fontSize="sm"
                  sx={{
                    p: { marginBottom: "0.8em" },
                    "p:last-child": { marginBottom: 0 },
                    strong: {
                      fontWeight: "bold",
                      color: msg.role === "user" ? "white" : "blue.600",
                    },
                    "ul, ol": { paddingLeft: "1.5em", marginBottom: "0.8em" },
                    li: { marginBottom: "0.3em" },
                    "h1, h2, h3": {
                      fontWeight: "bold",
                      marginTop: "1em",
                      marginBottom: "0.5em",
                    },
                  }}
                >
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </Box>

                {msg.has_attachment && (
                  <Text
                    fontSize="xs"
                    mt={2}
                    fontStyle="italic"
                    color={msg.role === "user" ? "blue.100" : "gray.500"}
                  >
                    📎 Imagem/Arquivo anexado
                  </Text>
                )}

                <Box
                  position="absolute"
                  top="1"
                  right="-8"
                  opacity={0}
                  _groupHover={{ opacity: 1 }}
                  transition="opacity 0.2s"
                >
                  <Menu>
                    <MenuButton
                      as={IconButton}
                      icon={<FiMoreVertical />}
                      size="xs"
                      variant="ghost"
                      aria-label="Opções"
                    />
                    <MenuList minW="100px">
                      <MenuItem
                        icon={<FiTrash2 />}
                        color="red.500"
                        onClick={() => handleSoftDelete(msg.id)}
                      >
                        Ocultar
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </Box>
              </Flex>
            </Flex>
          ))}
          {isLoading && (
            <Flex justify="flex-start" mb={4}>
              <Flex
                bg="chat.agentMsgBg"
                p={3}
                borderRadius="lg"
                boxShadow="sm"
                border="1px solid"
                borderColor="chat.borderColor"
                align="center"
              >
                <Spinner size="sm" color="blue.500" mr={2} />
                <Text fontSize="sm" color="chat.mutedText">
                  {" "}
                  Dr. EpiScope está analisando...
                </Text>
              </Flex>
            </Flex>
          )}
          <div ref={messagesEndRef} />
        </Flex>

        <Flex
          p={4}
          bg="chat.inputAreaBg"
          borderTop="1px solid"
          borderColor="chat.borderColor"
          align="center"
        >
          <input
            type="file"
            id="file-upload"
            style={{ display: "none" }}
            onChange={handleFileChange}
            accept="image/*"
          />
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
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            variant="filled"
            bg="chat.inputBg"
            _focus={{ bg: "chat.inputBg", borderColor: "blue.400" }}
          />
          <IconButton
            icon={<FiSend />}
            colorScheme="blue"
            ml={2}
            onClick={handleSendMessage}
            isLoading={isLoading}
            aria-label="Enviar"
          />
        </Flex>
      </Flex>
    </Box>
  );
};

export default AgentChat;
