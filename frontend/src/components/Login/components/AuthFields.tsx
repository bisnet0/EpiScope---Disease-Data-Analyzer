import React from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
} from "@chakra-ui/react";
import type { AuthFieldsProps } from "../types";

export const AuthFields: React.FC<AuthFieldsProps> = ({
  state,
  setters,
  actions,
}) => {
  return (
    <Box as="form" onSubmit={actions.handleSubmit} w="100%">
      <VStack spacing={4} align="flex-start">
        {/* 👇 TUDO QUE ESTÁ AQUI DENTRO SÓ APARECE NO REGISTRO */}
        {!state.isLogin && (
          <>
            <FormControl isRequired>
              <FormLabel htmlFor="username">Usuário</FormLabel>
              <Input
                id="username"
                type="text"
                value={state.username}
                onChange={(e) => setters.setUsername(e.target.value)}
                placeholder="Seu nome de usuário"
                focusBorderColor="blue.400"
              />
            </FormControl>

            <FormControl isRequired>
              <FormLabel htmlFor="inviteCode">Código de Convite</FormLabel>
              <Input
                id="inviteCode"
                type="text"
                value={state.inviteCode}
                onChange={(e) =>
                  setters.setInviteCode(e.target.value.toUpperCase())
                }
                focusBorderColor="blue.400"
              />
            </FormControl>
          </>
        )}
        {/* 👆 FIM DA ÁREA EXCLUSIVA DE REGISTRO */}

        {/* 👇 Estes dois (Email e Senha) ficam de fora pois aparecem em ambos (Login e Registro) */}
        <FormControl isRequired>
          <FormLabel htmlFor="email">E-mail</FormLabel>
          <Input
            id="email"
            type="email"
            value={state.email}
            onChange={(e) => setters.setEmail(e.target.value)}
            placeholder="seu_email@gmail.com"
            focusBorderColor="blue.400"
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel htmlFor="password">Senha</FormLabel>
          <Input
            id="password"
            type="password"
            value={state.password}
            onChange={(e) => setters.setPassword(e.target.value)}
            placeholder="********"
            focusBorderColor="blue.400"
          />
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          size="lg"
          w="full"
          mt={4}
          isLoading={state.loading}
          loadingText="Processando..."
        >
          {state.isLogin ? "Entrar" : "Cadastrar"}
        </Button>
      </VStack>
    </Box>
  );
};
