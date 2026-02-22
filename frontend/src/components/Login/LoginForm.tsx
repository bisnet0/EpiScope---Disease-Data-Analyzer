import React from 'react';
import { Box, Flex, Heading, Text, Alert, AlertIcon } from '@chakra-ui/react';
import { useAuthForm } from './hooks/useAuthForm';
import { AuthFields } from './components/AuthFields';
import { AuthToggle } from './components/AuthToggle';
import { useLoginThemeFx } from './styles/theme-fx';

export const LoginForm: React.FC = () => {
  const { state, setters, actions } = useAuthForm();
  const themeFx = useLoginThemeFx(); // <-- Consumindo os estilos centralizados

  return (
    <Flex 
      minH="100vh" 
      align="center" 
      justify="center" 
      bgGradient={themeFx.bgGradient}
      p={4}
    >
      <Box
        w="full"
        maxW="md"
        bg={themeFx.cardBg}
        p={8}
        borderRadius="xl"
        boxShadow="xl"
        border="1px solid"
        borderColor={themeFx.cardBorder}
        backdropFilter="blur(16px)"
        transition="all 0.3s ease"
      >
        
        <Box textAlign="center" mb={8}>
          <Heading fontSize="2xl" fontWeight="bold">
            {state.isLogin ? 'Bem-vindo ao EpiScope' : 'Crie sua conta'}
          </Heading>
          <Text fontSize="md" color={themeFx.textMuted} mt={2}>
            {state.isLogin 
              ? 'Faça login para acessar seus diagnósticos' 
              : 'Registre-se para salvar seu histórico médico'}
          </Text>
        </Box>

        {state.error && (
          <Alert status="error" mb={6} borderRadius="md">
            <AlertIcon />
            {state.error}
          </Alert>
        )}

        <AuthFields state={state} setters={setters} actions={actions} />
        <AuthToggle isLogin={state.isLogin} onToggle={actions.toggleMode} />
        
      </Box>
    </Flex>
  );
};