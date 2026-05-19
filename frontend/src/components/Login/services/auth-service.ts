import api from "../../../middleware/api";
import { type AuthPayload, type AuthResponse } from "../types";

export const loginApi = async (payload: AuthPayload): Promise<AuthResponse> => {
  const response = await api.post("/auth/login", payload);
  return response.data;
};

export const registerApi = async (
  payload: AuthPayload,
): Promise<AuthResponse> => {
  const response = await api.post("/auth/register", payload);
  return response.data;
};
export const userService = {
  // Busca as informações do usuário atual (incluindo a hide_surgery_warning)
  getMe: async () => {
    const response = await api.get("/auth/me");
    return response.data;
  },

  // Atualiza as preferências do usuário
  updatePreferences: async (preferences: { hide_surgery_warning: boolean }) => {
    const response = await api.patch("/auth/preferences", preferences);
    return response.data;
  },
};
