import React from 'react';

interface Props {
  isLogin: boolean;
  onToggle: () => void;
}

export const AuthToggle: React.FC<Props> = ({ isLogin, onToggle }) => {
  return (
    <p className="toggle-text">
      {isLogin ? "Não tem uma conta? " : "Já tem uma conta? "}
      <span onClick={onToggle} style={{ cursor: 'pointer', fontWeight: 'bold' }}>
        {isLogin ? "Registre-se" : "Faça Login"}
      </span>
    </p>
  );
};