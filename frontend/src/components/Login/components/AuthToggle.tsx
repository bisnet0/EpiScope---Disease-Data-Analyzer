import React from 'react';
import { Text, Link } from '@chakra-ui/react';
import { useLoginThemeFx } from '../styles/theme-fx';
import type { AuthToggleProps } from '../types';


export const AuthToggle: React.FC<AuthToggleProps> = ({ isLogin, onToggle }) => {
  const { textMuted, linkColor } = useLoginThemeFx();

  return (
    <Text textAlign="center" mt={6} fontSize="sm" color={textMuted}>
      {isLogin ? "Não tem uma conta? " : "Já tem uma conta? "}
      <Link 
        color={linkColor} 
        fontWeight="bold" 
        onClick={onToggle}
        _hover={{ textDecoration: 'underline' }}
      >
        {isLogin ? "Registre-se" : "Faça Login"}
      </Link>
    </Text>
  );
};