import React from "react";
import { Box, Text, VStack } from "@chakra-ui/react";
import Toast from "../../components/Toast/Toast";
import { useDAppLedger } from "./hooks/useDAppLedger";
import { DAppHeader } from "./components/DAppHeader";
import { HistoryTable } from "./components/HistoryTable";
import { useDAppThemeFx } from "./styles/theme-fx";

export const DiagnosisDAppForm: React.FC = () => {
  const { state, auth, actions } = useDAppLedger();
  const themeFx = useDAppThemeFx();

  return (
    <Box w="full" maxW="1800px" mx="auto" pb={10}>
      <VStack spacing={6} align="stretch" w="full">
        <Box
          bg={themeFx.cardBg}
          p={{ base: 4, md: 8 }}
          borderRadius="xl"
          border="1px solid"
          borderColor={themeFx.cardBorder}
          backdropFilter="blur(16px)"
          boxShadow="lg"
          w="full"
          overflow="hidden"
        >
          <DAppHeader
            walletAddress={auth.walletAddress}
            connectWallet={auth.connectWallet}
          />

          <Text
            color={themeFx.mutedText}
            fontSize={{ base: "sm", md: "md" }}
            mb={8}
            lineHeight="1.6"
          >
            Selecione um diagnóstico do seu histórico Web2 para enviar para a
            camada de execução verificável (Cartesi Machine). Isso cria uma
            prova criptográfica imutável do resultado.
          </Text>

          {state.loading ? (
            <Text textAlign="center" color={themeFx.mutedText} py={10}>
              Carregando histórico...
            </Text>
          ) : (
            <Box animation="fade-in 0.5s" w="full">
              {/* O HistoryTable com seus 2 Boxes aninhados continua sendo essencial aqui! */}
              <HistoryTable
                history={state.history}
                walletAddress={auth.walletAddress}
                sendingId={state.sendingId}
                onRegisterOnChain={actions.handleRegisterOnChain}
              />
            </Box>
          )}
        </Box>
      </VStack>

      {state.toast && (
        <Toast
          type={state.toast.type}
          message={state.toast.message}
          onClose={actions.closeToast}
          title={state.toast.title}
        />
      )}
    </Box>
  );
};
