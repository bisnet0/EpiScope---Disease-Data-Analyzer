export interface AuthPayload {
  email: string;
  password: string;
  username?: string;
  invite_code?: string;
}

export interface AuthResponse {
  user: any; // Substitua 'any' pela tipagem real do seu usuário, ex: { id: string, name: string... }
  token?: string;
}

export interface AuthFieldsProps {
  state: any;
  setters: any;
  actions: any;
}

export interface AuthToggleProps {
  isLogin: boolean;
  onToggle: () => void;
}
