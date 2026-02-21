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