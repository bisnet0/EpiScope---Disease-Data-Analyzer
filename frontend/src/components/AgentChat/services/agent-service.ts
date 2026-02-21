import api from "../../../middleware/api";
import { type Message, type ChatResponse, type ChatPayload } from "../types";

export const fetchChatHistory = async (): Promise<Message[]> => {
  const response = await api.get<Message[]>("/agent/history");
  return response.data;
};

export const sendChatMessageApi = async (payload: ChatPayload): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>("/agent/chat", payload);
  return response.data;
};