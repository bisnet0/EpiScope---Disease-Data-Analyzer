import {
  useState,
  useEffect,
  useRef,
  useCallback,
  type ChangeEvent,
  type KeyboardEvent,
} from "react";
import {
  fetchChatHistory,
  sendChatMessageApi,
} from "../services/agent-service";
import { type Message } from "../types";
import { useToast } from "../../Toast/components/ToastContext";

export const useAgentChat = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const [attachment, setAttachment] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { showToast } = useToast();

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const handleEmergency = async (event: any) => {
      const detail = event.detail;
      if (!detail?.diagnosis) return;

      setIsOpen(true);
      setIsLoading(true);

      try {
        const context = detail.consultationType || "TRIAGEM_VIOLENCIA";

        const emergencyContent = `🚨 **ALERTA DE EMERGÊNCIA ATIVADO** 🚨\n\nIdentifiquei um quadro de atenção severa:\n*"${detail.diagnosis}"*\n\nJá iniciei a auditoria. **Dr. EpiScope**, por favor, acesse os dados cruzados da paciente (utilize a ferramenta 'fetch_womens_health_biomarkers' para o contexto "${context}").\n\nAnalisando o áudio e o vídeo juntos, como devo conduzir o protocolo de acolhimento agora?`;

        await sendChatMessageApi({
          message: emergencyContent,
          attachment: null,
        });

        const history = await fetchChatHistory();
        setMessages(history);
      } catch (error) {
        console.error("❌ Erro ao persistir alerta:", error);
      } finally {
        setIsLoading(false);
        scrollToBottom();
      }
    };

    window.addEventListener("openMaestroChat", handleEmergency);
    return () => window.removeEventListener("openMaestroChat", handleEmergency);
  }, [showToast]);

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
        showToast({
          type: "success",
          message: "Arquivo anexado",
          title: "Sucesso",
          duration: 3000,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleInputChange = (value: string) => {
    setInputValue(value);
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
    } catch (error: any) {
      if (
        error.response?.status === 429 ||
        error.response?.data?.error === "QUOTA_EXCEEDED"
      ) {
        showToast({
          title: "Doutor descansando 💤",
          message:
            "O limite gratuito da API do Google Gemini foi atingido. O Dr. EpiScope volta a atender assim que a cota resetar.",
          type: "info",
          duration: 6000,
        });
      } else {
        showToast({
          title: "Erro de comunicação",
          message: "O Dr. EpiScope está indisponível no momento.",
          type: "error",
          duration: 3000,
        });
      }
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
    showToast({
      title: "Mensagem ocultada",
      message: "Ela ainda está salva no histórico do sistema.",
      type: "info",
      duration: 3000,
    });
  };

  return {
    state: {
      isOpen,
      messages,
      inputValue,
      attachment,
      isLoading,
      messagesEndRef,
    },
    setters: { setIsOpen },
    actions: {
      handleFileChange,
      handleSendMessage,
      handleKeyPress,
      handleSoftDelete,
      handleInputChange,
    },
  };
};
