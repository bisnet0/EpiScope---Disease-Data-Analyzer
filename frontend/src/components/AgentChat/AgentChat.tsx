import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import { useAgentChat } from "./hooks/useAgentChat";
import { ChatToggleButton } from "./components/ChatToggleButton";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessageList } from "./components/ChatMessageList";
import { ChatInputArea } from "./components/ChatInputArea";

const AgentChat: React.FC = () => {
  const { state, setters, actions } = useAgentChat();

  if (!state.isOpen) {
    return <ChatToggleButton onOpen={() => setters.setIsOpen(true)} />;
  }

  return (
    <Box position="fixed" bottom="20px" right={{ base: "10px", md: "20px" }} zIndex={1000}>
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