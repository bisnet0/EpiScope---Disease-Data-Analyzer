// src/context/AuthContext.tsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from "jwt-decode";
import type { ReactNode } from 'react';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextData {
  user: User | null;
  token: string | null;
  signIn: (token: string, userData: User) => void;
  signOut: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Ao carregar a página, verifica se tem token salvo
    const storedToken = localStorage.getItem('@EpiScope:token');
    const storedUser = localStorage.getItem('@EpiScope:user');

    if (storedToken && storedUser) {
      // Opcional: Verificar se o token expirou usando jwt-decode
      try {
        const decoded: any = jwtDecode(storedToken);
        if (decoded.exp * 1000 < Date.now()) {
            signOut();
        } else {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
      } catch {
        signOut();
      }
    }
  }, []);

  const signIn = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('@EpiScope:token', newToken);
    localStorage.setItem('@EpiScope:user', JSON.stringify(newUser));
  };

  const signOut = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('@EpiScope:token');
    localStorage.removeItem('@EpiScope:user');
  };

  return (
    <AuthContext.Provider value={{ user, token, signIn, signOut, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);