export interface AuthPayload {
  email: string;
  password: string;
  username?: string;
}

export interface AuthResponse {
  user: any; // Substitua 'any' pela tipagem real do seu usuário, ex: { id: string, name: string... }
  token?: string;
}