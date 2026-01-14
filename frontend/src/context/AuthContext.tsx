import React, { createContext, useState, useEffect, useContext, type ReactNode } from 'react';
import { ethers } from 'ethers';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

interface User {
id: string;
  username: string;
  email: string;
}

interface AuthContextData {
  user: User | null;
  signIn: (userData: User) => void;
  signOut: () => Promise<void>;
  isAuthenticated: boolean;
  loadingAuth: boolean;


  walletAddress: string | null;
  connectWallet: () => Promise<void>;
  signer: ethers.JsonRpcSigner | null;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const navigate = useNavigate();


  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [signer, setSigner] = useState<ethers.JsonRpcSigner | null>(null);

useEffect(() => {
  const checkSession = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
      checkWalletConnection();
    } catch (error) {
      setUser(null);
      navigate('/login', { replace: true });
    } finally {
      setLoadingAuth(false);
    }
  };

  checkSession();
}, [navigate]);




  const checkWalletConnection = async () => {
    if (window.ethereum) {
      try {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const accounts = await provider.listAccounts();
        if (accounts.length > 0) {
          const s = await provider.getSigner();
          setWalletAddress(accounts[0].address);
          setSigner(s);
        }
      } catch (err) { console.error("Erro Web3:", err); }
    }
  };

  const connectWallet = async () => {
    if (!window.ethereum) return alert("MetaMask não encontrada!");
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      await provider.send("eth_requestAccounts", []);
      const s = await provider.getSigner();
      setWalletAddress(await s.getAddress());
      setSigner(s);
    } catch (error) { console.error("Erro conectar wallet:", error); }
  };


  const signIn = (userData: User) => {
    setUser(userData);
  };

const signOut = async () => {
  try {
    await api.post('/auth/logout');
  } catch (e) {
    console.error(e);
  }

  setUser(null);
  setWalletAddress(null);
  setSigner(null);
  navigate('/login', { replace: true });
};


  return (
    <AuthContext.Provider value={{
      user, signIn, signOut, isAuthenticated: !!user, loadingAuth,
      walletAddress, connectWallet, signer
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);