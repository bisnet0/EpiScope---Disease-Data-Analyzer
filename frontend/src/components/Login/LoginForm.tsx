import React from "react";
import { Box, Heading, Text, Alert, AlertIcon } from "@chakra-ui/react";
import { useAuthForm } from "./hooks/useAuthForm";
import { AuthFields } from "./components/AuthFields";
import { AuthToggle } from "./components/AuthToggle";
import { useLoginThemeFx } from "./styles/theme-fx";
import Toast from "../Toast/Toast";

export const LoginForm: React.FC = () => {
  const { state, setters, actions } = useAuthForm();
  const themeFx = useLoginThemeFx();

  return (
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
      mx="auto"
    >
      <Box textAlign="center" mb={8}>
        <Heading fontSize="2xl" fontWeight="bold" color={themeFx.textColor}>
          {state.isLogin ? "Entre agora no EpiScope AI" : "Crie sua conta"}
        </Heading>
        <Text fontSize="md" color={themeFx.textMuted} mt={2}>
          {state.isLogin
            ? "Faça login para acessar seus diagnósticos"
            : "Registre-se para salvar seu histórico médico"}
        </Text>
      </Box>

      {state.error && (
        <Toast
          type="error"
          title={state.isLogin ? "Erro ao fazer login" : "Erro ao criar conta"}
          message={state.error}
          duration={4000}
          onClose={() => {
            setters.setError(null);
          }}
        />
      )}

      <AuthFields state={state} setters={setters} actions={actions} />
      <AuthToggle isLogin={state.isLogin} onToggle={actions.toggleMode} />
    </Box>
  );
};
