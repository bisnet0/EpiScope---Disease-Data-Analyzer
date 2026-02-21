import React, { MutableRefObject } from "react";
import { Flex, Box, Text, Menu, MenuButton, MenuList, MenuItem, IconButton, Spinner } from "@chakra-ui/react";
import { FiMoreVertical, FiTrash2 } from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import { Message } from "../types";

interface Props {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: MutableRefObject<HTMLDivElement | null>;
  onSoftDelete: (id: string) => void;
}

export const ChatMessageList: React.FC<Props> = ({ messages, isLoading, messagesEndRef, onSoftDelete }) => (
  <Flex flex={1} direction="column" p={4} overflowY="auto" bg="chat.areaBg">
    {messages.map((msg) => (
      <Flex key={msg.id} justify={msg.role === "user" ? "flex-end" : "flex-start"} mb={4}>
        <Flex
          maxW="80%"
          bg={msg.role === "user" ? "blue.500" : "chat.agentMsgBg"}
          color={msg.role === "user" ? "white" : "chat.agentMsgText"}
          p={3}
          borderRadius="lg"
          boxShadow="sm"
          border={msg.role === "agent" ? "1px solid" : "none"}
          borderColor={msg.role === "agent" ? "chat.borderColor" : "transparent"}
          position="relative"
          role="group"
        >
          <Box
            fontSize="sm"
            sx={{
              p: { marginBottom: "0.8em" },
              "p:last-child": { marginBottom: 0 },
              strong: { fontWeight: "bold", color: msg.role === "user" ? "white" : "blue.600" },
              "ul, ol": { paddingLeft: "1.5em", marginBottom: "0.8em" },
              li: { marginBottom: "0.3em" },
              "h1, h2, h3": { fontWeight: "bold", marginTop: "1em", marginBottom: "0.5em" },
            }}
          >
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </Box>

          {msg.has_attachment && (
            <Text fontSize="xs" mt={2} fontStyle="italic" color={msg.role === "user" ? "blue.100" : "gray.500"}>
              📎 Imagem/Arquivo anexado
            </Text>
          )}

          <Box position="absolute" top="1" right="-8" opacity={0} _groupHover={{ opacity: 1 }} transition="opacity 0.2s">
            <Menu>
              <MenuButton as={IconButton} icon={<FiMoreVertical />} size="xs" variant="ghost" aria-label="Opções" />
              <MenuList minW="100px">
                <MenuItem icon={<FiTrash2 />} color="red.500" onClick={() => onSoftDelete(msg.id)}>
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
        <Flex bg="chat.agentMsgBg" p={3} borderRadius="lg" boxShadow="sm" border="1px solid" borderColor="chat.borderColor" align="center">
          <Spinner size="sm" color="blue.500" mr={2} />
          <Text fontSize="sm" color="chat.mutedText">Dr. EpiScope está analisando...</Text>
        </Flex>
      </Flex>
    )}
    <div ref={messagesEndRef} />
  </Flex>
);