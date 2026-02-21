import { useState, useEffect, useRef, ChangeEvent, KeyboardEvent } from "react";
import { useToast } from "@chakra-ui/react";
import { fetchChatHistory, sendChatMessageApi } from "../../../middleware/agent-service";
import { Message } from "../types";

export const useAgentChat = () => {
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
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    try {
      const history = await fetchChatHistory();
      setMessages(history);
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
    
    const currentInput = inputValue;
    const currentAttachment = attachment;
    
    setInputValue("");
    setAttachment(null);
    setIsLoading(true);

    try {
      const data = await sendChatMessageApi({
        message: currentInput,
        attachment: currentAttachment,
      });

      const agentMsg: Message = {
        id: data.msg_id,
        role: "agent",
        content: data.response,
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

  return {
    state: { isOpen, messages, inputValue, attachment, isLoading, messagesEndRef },
    setters: { setIsOpen, setInputValue },
    actions: { handleFileChange, handleSendMessage, handleKeyPress, handleSoftDelete }
  };
};