import React, { useState } from "react";
import {
  Box,
  Heading,
  Text,
  HStack,
  Button,
  Input,
  IconButton,
  useColorModeValue,
} from "@chakra-ui/react";
import axios from "axios";
import { Copy, Key } from "react-bootstrap-icons";
import { useToast } from "../../Toast/components/ToastContext";

interface InviteGeneratorProps {
  userRole: string;
}

export const InviteGenerator: React.FC<InviteGeneratorProps> = ({
  userRole,
}) => {
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const { showToast } = useToast();

  // Cores dinâmicas para o texto acompanhando o Dark/Light mode
  const textMuted = useColorModeValue("gray.600", "gray.400");
  const textColor = useColorModeValue("gray.800", "white");

  // Trava de segurança no render
  if (userRole !== "admin") return null;

  const handleGenerateKey = async () => {
    setIsGenerating(true);
    try {
      const response = await axios.post(
        "/api/auth/generate-invite",
        {},
        {
          withCredentials: true,
        },
      );
      setGeneratedKey(response.data.code);
      showToast({
        title: "Chave-mestre gerada!",
        message: "Compartilhe este código apenas com pessoas autorizadas.",
        type: "success",
        duration: 4000,
      });
    } catch (err: any) {
      showToast({
        title: "Acesso Negado",
        message: err.response?.data?.error || "Erro ao gerar a chave.",
        type: "error",
        duration: 5000,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (generatedKey) {
      navigator.clipboard.writeText(generatedKey);
      showToast({
        title: "Copiado!",
        message: "Chave copiada para a área de transferência.",
        type: "info",
        duration: 2000,
      });
    }
  };

  return (
    <Box
      p={6}
      bg="rgba(229, 62, 62, 0.05)"
      borderRadius="xl"
      border="1px solid"
      borderColor="red.500"
    >
      <Heading
        size="md"
        color="red.400"
        mb={2}
        display="flex"
        alignItems="center"
        gap={2}
      >
        <Key size={20} /> Painel Administrativo
      </Heading>
      <Text color={textMuted} mb={4} fontSize="sm">
        Gere chaves-mestre temporárias para permitir o cadastro de novos
        usuários na plataforma do EpiScope.
      </Text>

      <HStack spacing={4} flexWrap="wrap">
        <Button
          colorScheme="red"
          onClick={handleGenerateKey}
          isLoading={isGenerating}
          loadingText="Gerando..."
        >
          Gerar Chave-Mestre
        </Button>

        {generatedKey && (
          <HStack flex={1} minW="200px">
            <Input
              value={generatedKey}
              isReadOnly
              fontFamily="monospace"
              borderColor="red.300"
              color={textColor}
              bg="whiteAlpha.200"
              _focus={{ borderColor: "red.400" }}
            />
            <IconButton
              aria-label="Copiar chave"
              icon={<Copy size={18} />}
              colorScheme="gray"
              variant="outline"
              borderColor="red.300"
              _hover={{ bg: "whiteAlpha.300" }}
              onClick={copyToClipboard}
            />
          </HStack>
        )}
      </HStack>
    </Box>
  );
};
