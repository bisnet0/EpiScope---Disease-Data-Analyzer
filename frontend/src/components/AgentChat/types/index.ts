import type { ChangeEvent, MutableRefObject, KeyboardEvent } from "react";

export interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  has_attachment?: boolean;
  created_at?: string;
}

export interface ChatResponse {
  response: string;
  msg_id: string;
  status: string;
}

export interface ChatPayload {
  message: string;
  attachment: string | null;
}

export interface ChatToggleButtonProps {
  onOpen: () => void;
}

export interface ChatHeaderProps {
  onClose: () => void;
}

export interface ChatMessageListProps {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: MutableRefObject<HTMLDivElement | null>;
  onSoftDelete: (id: string) => void;
}

export interface ChatInputAreaProps {
  inputValue: string;
  attachment: string | null;
  isLoading: boolean;
  onInputChange: (val: string) => void;
  onFileChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onSendMessage: () => void;
  onKeyPress: (e: KeyboardEvent<HTMLInputElement>) => void;
}