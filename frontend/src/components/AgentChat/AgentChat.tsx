import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import { useAgentChat } from "./hooks/useAgentChat";
import { ChatToggleButton } from "./components/ChatToggleButton";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessageList } from "./components/ChatMessageList";
import { ChatInputArea } from "./components/ChatInputArea";
import { useChatThemeFx } from "./styles/theme-fx";

const AgentChat: React.FC = () => {
  const { state, setters, actions } = useAgentChat();
  const themeFx = useChatThemeFx();

  if (!state.isOpen) {
    return <ChatToggleButton onOpen={() => setters.setIsOpen(true)} />;
  }

  return (
    <Box position="fixed" bottom="20px" right={{ base: "10px", md: "20px" }} zIndex={1000} animation="fade-in 0.3s">
      <Flex
        w={{ base: "calc(100vw - 20px)", md: "400px", lg: "450px" }} // Ajustei a largura para ficar mais com cara de "Widget"
        height={{ base: "calc(100vh - 100px)", md: "600px" }}
        flexDirection="column"
        borderRadius="xl"
        bg={themeFx.containerBg}
        boxShadow="0 20px 40px -4px rgba(0, 0, 0, 0.4)"
        overflow="hidden"
        border="1px solid"
        borderColor={themeFx.borderColor}
        backdropFilter="blur(20px)"
      >
        <ChatHeader onClose={() => setters.setIsOpen(false)} />

        <ChatMessageList
          messages={state.messages}
          isLoading={state.isLoading}
          messagesEndRef={state.messagesEndRef}
          onSoftDelete={actions.handleSoftDelete}
        />

        <ChatInputArea
          inputValue={state.inputValue}
          attachment={state.attachment}
          isLoading={state.isLoading}
          onInputChange={setters.setInputValue}
          onFileChange={actions.handleFileChange}
          onSendMessage={actions.handleSendMessage}
          onKeyPress={actions.handleKeyPress}
        />
      </Flex>
    </Box>
  );
};

export default AgentChat;