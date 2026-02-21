import api from "./api";
import { AuthPayload, AuthResponse } from "../components/Login/types"; // Ajuste o caminho

export const loginApi = async (payload: AuthPayload): Promise<AuthResponse> => {
  const response = await api.post("/auth/login", payload);
  return response.data;
};

export const registerApi = async (payload: AuthPayload): Promise<AuthResponse> => {
  const response = await api.post("/auth/register", payload);
  return response.data;
};