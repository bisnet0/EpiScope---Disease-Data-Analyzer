import { useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { loginApi, registerApi } from '../../../services/auth-service';
import { AuthPayload } from '../types';

export const useAuthForm = () => {
  const { signIn } = useAuth();
  
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const payload: AuthPayload = isLogin 
      ? { email, password } 
      : { username, email, password };

    try {
      const data = isLogin ? await loginApi(payload) : await registerApi(payload);

      if (data && data.user) {
        signIn(data.user);
      }
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || "Erro na conexão";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return {
    state: { isLogin, email, password, username, error, loading },
    setters: { setEmail, setPassword, setUsername },
    actions: { handleSubmit, toggleMode }
  };
};