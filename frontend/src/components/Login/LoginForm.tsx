import React from 'react';
import { useAuthForm } from './hooks/useAuthForm';
import { AuthFields } from './components/AuthFields';
import { AuthToggle } from './components/AuthToggle';
import './LoginForm.css';

export const LoginForm: React.FC = () => {
  const { state, setters, actions } = useAuthForm();

  return (
    <div className="login-container">
      <div className="login-card">
        
        <h2>{state.isLogin ? 'Bem-vindo ao EpiScope' : 'Crie sua conta'}</h2>
        <p className="subtitle">
          {state.isLogin 
            ? 'Faça login para acessar seus diagnósticos' 
            : 'Registre-se para salvar seu histórico médico'}
        </p>

        {state.error && <div className="error-msg">{state.error}</div>}

        <AuthFields state={state} setters={setters} actions={actions} />

        <AuthToggle isLogin={state.isLogin} onToggle={actions.toggleMode} />
        
      </div>
    </div>
  );
};