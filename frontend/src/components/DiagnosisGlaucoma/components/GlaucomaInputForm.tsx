import React, { type ChangeEvent } from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Image,
  Center,
  Text,
  keyframes,
  Icon,
} from "@chakra-ui/react";
import { useGlaucomaThemeFx } from "../styles/theme-fx";
import { type GlaucomaInputFormProps } from "../types";
import { EyeFill, EyeSlash } from "react-bootstrap-icons";
import { BsEye } from "react-icons/bs";

export const GlaucomaInputForm: React.FC<GlaucomaInputFormProps> = ({
  previewUrl,
  loading,
  onImageChange,
  onSubmit,
}) => {
   const pulse = keyframes`
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    `;
  const themeFx = useGlaucomaThemeFx();

  return (
    <Box
      as="form"
      onSubmit={onSubmit}
      bg={themeFx.cardBg}
      p={{ base: 5, md: 8 }}
      borderRadius="xl"
      border="1px solid"
      borderColor={themeFx.cardBorder}
      backdropFilter="blur(16px)"
      boxShadow="lg"
      w="full"
    >
      <VStack spacing={5} align="stretch">
        <Heading size="md" display="flex" alignItems="center" color={themeFx.textColor}>
        <Icon as={BsEye} color={themeFx.eyeColor} mr={3} w={6} h={6} />
        Análise de Imagem para Glaucoma
      </Heading>

        <FormControl isRequired>
          <FormLabel color={themeFx.textColor}>
            Imagem do fundo do olho:
          </FormLabel>
          <Input
            type="file"
            accept="image/*"
            onChange={onImageChange}
            bg={themeFx.inputBg}
            p={1} // Padding reduzido para ajustar o botão nativo do browser dentro do Input
            focusBorderColor="pink.400"
            sx={{
              "::file-selector-button": {
                height: "100%",
                mr: 4,
                border: "none",
                background: "transparent",
                fontWeight: "bold",
                color: "pink.500",
                cursor: "pointer",
              },
            }}
          />
        </FormControl>

        {previewUrl && (
          <Center mb={2}>
            <Image
              src={previewUrl}
              alt="Preview"
              maxW="200px"
              borderRadius="md"
              border="2px solid"
              borderColor="pink.400"
              boxShadow="md"
            />
          </Center>
        )}

        <Button
          type="submit"
          colorScheme="pink"
          size="lg"
          isLoading={loading}
          loadingText="Consultando Maestro e Auditoria..."
        >
          Enviar Imagem
        </Button>
        {loading && (
          <Text
            fontSize="xs"
            color="pink.500"
            textAlign="center"
            animation={`${pulse} 1.5s infinite`} // Certifique-se de definir o keyframes 'pulse' aqui também
          >
            ⚙️ Processando Redes Neurais e registrando Auditoria...
          </Text>
        )}
      </VStack>
    </Box>
  );
};
