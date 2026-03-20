import React, { useRef } from "react";
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
  VStack,
  Image,
  Input,
  Icon,
  Progress,
  Badge,
  Divider,
} from "@chakra-ui/react";
import { CloudUpload, Activity } from "react-bootstrap-icons";
import { useXRay } from "../hooks/useXRay";
import { useXRayThemeFx } from "../styles/theme-fx";

export const DiagnosisXRayForm: React.FC = () => {
  const { state, actions } = useXRay();
  const themeFx = useXRayThemeFx();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleBoxClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
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
      <Heading
        size="md"
        mb={2}
        color={themeFx.textColor}
        display="flex"
        alignItems="center"
        gap={3}
      >
        <Icon as={Activity} color={themeFx.accentColor} />
        Análise de Raio-X Pulmonar
        <Badge
          colorScheme="cyan"
          variant="solid"
          borderRadius="md"
          px={2}
          py={0.5}
        >
          BETA
        </Badge>
      </Heading>

      <Text color={themeFx.mutedText} mb={8}>
        Faça o upload de uma radiografia de tórax para detecção de Pneumonia e
        anomalias pulmonares utilizando Redes Neurais Convolucionais (CNN).
      </Text>

      <Flex gap={8} direction={{ base: "column", lg: "row" }}>
        {/* --- COLUNA ESQUERDA: UPLOAD --- */}
        <Box flex="1" bg={themeFx.cardSoftBg} borderRadius={16} p={6}>
          <VStack spacing={6}>
            <Box
              w="100%"
              h="380px"
              border="2px dashed"
              borderColor={state.previewUrl ? themeFx.accentColor : "gray.500"}
              borderRadius="xl"
              display="flex"
              alignItems="center"
              justifyContent="center"
              cursor="pointer"
              onClick={handleBoxClick}
              position="relative"
              overflow="hidden"
              _hover={{ borderColor: themeFx.accentHover, bg: "whiteAlpha.50" }}
              transition="all 0.2s"
            >
              <Input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                onChange={actions.handleImageChange}
                display="none"
              />

              {state.previewUrl ? (
                <Image
                  src={state.previewUrl}
                  alt="Raio-X Preview"
                  objectFit="contain"
                  w="100%"
                  h="100%"
                />
              ) : (
                <VStack color={themeFx.mutedText} spacing={3}>
                  <Icon
                    as={CloudUpload}
                    boxSize={12}
                    color={themeFx.accentColor}
                  />
                  <Text fontWeight="medium" fontSize="lg">
                    Clique para buscar o Raio-X
                  </Text>
                  <Text fontSize="xs">Suporta JPG, PNG</Text>
                </VStack>
              )}
            </Box>

            <Button
              w="full"
              size="lg"
              onClick={actions.submitDiagnosis}
              isLoading={state.loading}
              loadingText="Analisando Tensores Pulmonares..."
              isDisabled={!state.previewUrl}
              bgGradient="linear(to-r, cyan.500, blue.500)"
              color="white"
              _hover={{ bgGradient: "linear(to-r, cyan.600, blue.600)" }}
            >
              Diagnosticar Imagem
            </Button>

            {state.error && (
              <Text color="red.400" fontSize="sm" textAlign="center">
                {state.error}
              </Text>
            )}
          </VStack>
        </Box>

        {/* --- COLUNA DIREITA: RESULTADOS --- */}
        <Box flex="1" bg={themeFx.cardSoftBg} borderRadius={16} p={6}>
          <Heading size="md" mb={4} color={themeFx.textColor}>
            Laudo Preditivo
          </Heading>
          <Divider mb={4} borderColor={themeFx.cardBorder} />

          {!state.result && !state.loading && (
            <Flex
              h="200px"
              align="center"
              justify="center"
              color={themeFx.mutedText}
              direction="column"
            >
              <Icon as={Activity} boxSize={8} mb={3} opacity={0.3} />
              <Text>Aguardando imagem para análise radiológica.</Text>
            </Flex>
          )}

          {state.loading && (
            <VStack spacing={4} mt={10}>
              <Text color={themeFx.textColor}>
                Processando matrizes de convolução...
              </Text>
              <Progress
                size="xs"
                isIndeterminate
                colorScheme="cyan"
                w="full"
                borderRadius="full"
              />
            </VStack>
          )}

          {state.result && (
            <VStack spacing={6} align="stretch">
              <Box
                p={4}
                borderRadius="md"
                bg={
                  state.result.prediction === "Normal" ? "green.500" : "red.500"
                }
                color="white"
                textAlign="center"
              >
                <Text
                  fontSize="xs"
                  fontWeight="bold"
                  textTransform="uppercase"
                  letterSpacing="wider"
                  mb={1}
                >
                  Diagnóstico Principal
                </Text>
                <Heading size="lg">{state.result.prediction}</Heading>
              </Box>

              <Box>
                <Text fontWeight="bold" color={themeFx.textColor} mb={3}>
                  Probabilidades Clínicas:
                </Text>
                {Object.entries(
                  state.result.analysis_details.probabilities,
                ).map(([key, value]) => {
                  const prob = (value as number) * 100;
                  return (
                    <Box key={key} mb={4}>
                      <Flex justify="space-between" mb={1}>
                        <Text color={themeFx.mutedText} fontSize="sm">
                          {key}
                        </Text>
                        <Text
                          color={themeFx.textColor}
                          fontWeight="bold"
                          fontSize="sm"
                        >
                          {prob.toFixed(1)}%
                        </Text>
                      </Flex>
                      <Progress
                        value={prob}
                        size="sm"
                        borderRadius="full"
                        colorScheme={
                          key === "Pneumonia"
                            ? themeFx.barPneumonia
                            : key === "Normal"
                              ? themeFx.barNormal
                              : themeFx.barTuberculosis
                        }
                      />
                    </Box>
                  );
                })}
              </Box>

              <Box
                p={4}
                bg="whiteAlpha.50"
                borderRadius="md"
                borderLeft="4px solid"
                borderColor={themeFx.accentColor}
              >
                <Text
                  fontSize="xs"
                  color={themeFx.accentColor}
                  mb={1}
                  fontWeight="bold"
                >
                  NOTAS DA INTELIGÊNCIA ARTIFICIAL:
                </Text>
                <Text
                  color={themeFx.textColor}
                  fontSize="sm"
                  fontStyle="italic"
                >
                  "{state.result.analysis_details.clinical_notes}"
                </Text>
              </Box>
            </VStack>
          )}
        </Box>
      </Flex>
    </Box>
  );
};
