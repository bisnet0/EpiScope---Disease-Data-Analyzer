// src/components/LoginForm.tsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './LoginForm.css'; // Vamos criar um CSS básico abaixo

export const LoginForm: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    const payload = isLogin 
        ? { email, password } 
        : { username, email, password };

    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erro na autenticação');
      }

      // Se for registro, fazemos o login automático ou pedimos para logar
      if (!isLogin) {
        setIsLogin(true);
        setError("Conta criada com sucesso! Faça login.");
        setLoading(false);
        return;
      }

      // Se for login, salva no contexto
      if (data.access_token && data.user) {
        signIn(data.access_token, data.user);
      }

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isLogin ? 'Bem-vindo ao EpiScope' : 'Crie sua conta'}</h2>
        <p className="subtitle">{isLogin ? 'Faça login para acessar seus diagnósticos' : 'Registre-se para salvar seu histórico médico'}</p>
        
        {error && <div className="error-msg">{error}</div>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Usuário</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)} required />
            </div>
          )}
          
          <div className="form-group">
            <label>E-mail</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Processando...' : (isLogin ? 'Entrar' : 'Cadastrar')}
          </button>
        </form>

        <p className="toggle-text">
          {isLogin ? "Não tem uma conta?" : "Já tem uma conta?"}
          <span onClick={() => { setIsLogin(!isLogin); setError(null); }}>
            {isLogin ? " Registre-se" : " Faça Login"}
          </span>
        </p>
      </div>
    </div>
  );
};