// src/features/DiagnosisWomensHealth/components/LaparoscopyAnalyzer.tsx
import React, { useRef } from "react";
import {
  Box,
  Flex,
  Text,
  Button,
  Heading,
  Icon,
  VStack,
  Center,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  Badge,
  HStack,
  Divider,
} from "@chakra-ui/react";
// Mudamos para Fa para combinar com o estilo do exemplo
import {
  FaVideo,
  FaFileVideo,
  FaCheckCircle,
  FaExclamationTriangle,
} from "react-icons/fa";
import { FiActivity } from "react-icons/fi";

// Usando o SEU hook de tema
import { useWomensHealthThemeFx } from "../styles/theme-fx";
import { useLaparoscopyAnalyzer } from "../hooks/useLaparoscopyAnalyzer";

export const LaparoscopyAnalyzer: React.FC = () => {
  const { selectedFile, isAnalyzing, result, handleFileChange, handleAnalyze } =
    useLaparoscopyAnalyzer();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Instanciando o SEU tema
  const theme = useWomensHealthThemeFx();

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // Calcula a porcentagem do sangramento
  const bleedingPercentage = result?.bleeding_ratio
    ? (result.bleeding_ratio * 100).toFixed(1)
    : "0.0";

  return (
    <VStack spacing={6} align="stretch" w="100%">
      {/* --- SEÇÃO DE UPLOAD (Seguindo o design do AudioAnalyzer) --- */}
      <Box
        p={5}
        bg={theme.innerBg}
        borderRadius="2xl"
        border="1px solid"
        borderColor={theme.cardBorder}
      >
        {/* HEADER */}
        <Flex align="center" justify="space-between" mb={4}>
          <Heading
            size="sm"
            color={theme.textColor}
            display="flex"
            alignItems="center"
          >
            {/* Usamos Azul para diferenciar de Áudio, mas mantemos o estilo */}
            <Icon as={FaVideo} mr={2} color="blue.400" />
            ANÁLISE CIRÚRGICA
          </Heading>
          <Text
            fontSize="xs"
            fontWeight="bold"
            color={theme.mutedText}
            textTransform="uppercase"
          >
            Laparoscopia
          </Text>
        </Flex>

        <VStack spacing={4} align="stretch">
          {/* DROPZONE / AREA DE SELEÇÃO */}
          <Center
            p={6}
            flexDirection="column"
            border="2px dashed"
            borderColor={selectedFile ? "blue.400" : theme.cardBorder}
            borderRadius="xl"
            bg={selectedFile ? "whiteAlpha.100" : "transparent"}
            cursor="pointer"
            transition="all 0.2s"
            _hover={{ borderColor: "blue.400", bg: "whiteAlpha.50" }}
            onClick={triggerFileInput}
          >
            <input
              type="file"
              accept="video/mp4,video/webm"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: "none" }}
            />

            {selectedFile ? (
              <VStack spacing={1}>
                <Icon
                  as={FaCheckCircle}
                  fontSize="3xl"
                  color="green.400"
                  mb={2}
                />
                <Text
                  fontWeight="bold"
                  color={theme.textColor}
                  textAlign="center"
                  noOfLines={1}
                >
                  {selectedFile.name}
                </Text>
                <Text fontSize="sm" color={theme.mutedText}>
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </Text>
              </VStack>
            ) : (
              <VStack spacing={2}>
                <Icon as={FaFileVideo} fontSize="3xl" color={theme.mutedText} />
                <Text color={theme.mutedText} textAlign="center" fontSize="sm">
                  Selecione o vídeo da cirurgia
                </Text>
              </VStack>
            )}
          </Center>

          {/* MENSAGEM DE ERRO (Se houver erro no objeto result) */}
          {result?.status === "error" && result.error && (
            <Flex
              align="center"
              p={3}
              bg="red.900"
              color="red.100"
              borderRadius="md"
              fontSize="sm"
            >
              <Icon as={FaExclamationTriangle} mr={2} />
              <Text>{result.error}</Text>
            </Flex>
          )}

          {/* BOTÃO DE AÇÃO / SPINNER (Idêntico ao estilo do exemplo) */}
          {isAnalyzing ? (
            <Flex align="center" justify="center" p={2} color="blue.400">
              <Spinner size="sm" mr={3} />
              <Text fontSize="sm" fontWeight="bold">
                YOLOv8 Analisando Frames...
              </Text>
            </Flex>
          ) : (
            <Button
              colorScheme="blue"
              size="md"
              width="full"
              onClick={handleAnalyze}
              isDisabled={!selectedFile}
              borderRadius="xl"
            >
              {result ? "Reanalisar Vídeo Cirúrgico" : "Iniciar Análise de IA"}
            </Button>
          )}
        </VStack>
      </Box>

      {/* --- SEÇÃO DE RESULTADOS (Também padronizada com o design novo) --- */}
      {result && result.status === "success" && (
        <Box
          p={5}
          bg={theme.innerBg}
          borderRadius="2xl"
          border="1px solid"
          borderColor={theme.cardBorder}
          animation="fade-in 0.5s"
        >
          {/* HEADER RESULTADOS */}
          <Flex align="center" justify="space-between" mb={5}>
            <Heading
              size="sm"
              color={theme.textColor}
              display="flex"
              alignItems="center"
            >
              <Icon as={FiActivity} mr={2} color="blue.400" />
              LAUDO DA IA CIRÚRGICA
            </Heading>
            <Badge colorScheme="green" borderRadius="full" px={3}>
              Concluído
            </Badge>
          </Flex>

          <VStack spacing={5} align="stretch">
            {/* Recomendação do Maestro (Integrado ao design) */}
            <Alert
              status="info"
              borderRadius="xl"
              bg="whiteAlpha.100"
              color={theme.textColor}
              variant="subtle"
            >
              <AlertIcon />
              <Box>
                <AlertTitle fontSize="sm">Recomendação do Maestro</AlertTitle>
                <AlertDescription fontSize="sm" color={theme.mutedText}>
                  {result.maestro_recommendation}
                </AlertDescription>
              </Box>
            </Alert>

            {/* Alertas Críticos (YOLO) */}
            {result.clinical_alerts && result.clinical_alerts.length > 0 && (
              <VStack align="stretch" spacing={2}>
                {result.clinical_alerts.map((alert, index) => (
                  <Flex
                    key={index}
                    align="center"
                    p={3}
                    bg="orange.900"
                    color="orange.100"
                    borderRadius="lg"
                    fontSize="sm"
                    fontWeight="medium"
                  >
                    <Icon as={FaExclamationTriangle} mr={2} />
                    <Text>{alert}</Text>
                  </Flex>
                ))}
              </VStack>
            )}

            {/* Estatísticas (Efeito de Card Interno) */}
            <Box
              p={4}
              borderRadius="xl"
              bg="whiteAlpha.50"
              border="1px solid"
              borderColor={theme.cardBorder}
            >
              <StatGroup>
                <Stat>
                  <StatLabel color={theme.mutedText}>Tempo</StatLabel>
                  <StatNumber color={theme.textColor}>
                    {result.total_analyzed_seconds}s
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel color={theme.mutedText}>
                    Risco Hemostático
                  </StatLabel>
                  <StatNumber
                    color={
                      Number(bleedingPercentage) > 20 ? "red.400" : "green.400"
                    }
                  >
                    {bleedingPercentage}%
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel color={theme.mutedText}>Procedimento</StatLabel>
                  <StatNumber color={theme.textColor} fontSize="md" mt={1}>
                    Laparoscopia
                  </StatNumber>
                </Stat>
              </StatGroup>
            </Box>

            <Divider borderColor={theme.cardBorder} />

            {/* Tags de Instrumentos Detectados */}
            <Box>
              <Text
                fontWeight="semibold"
                color={theme.mutedText}
                mb={3}
                fontSize="sm"
              >
                Telemetria de Objetos (Contagem de Frames)
              </Text>
              <HStack flexWrap="wrap" spacing={2}>
                {Object.entries(result.items_detected || {}).map(
                  ([item, count]) => (
                    <Badge
                      key={item}
                      px={3}
                      py={1}
                      borderRadius="full"
                      variant="subtle"
                      colorScheme={item === "bleeding" ? "red" : "blue"}
                      textTransform="capitalize"
                      fontSize="xs"
                    >
                      {item}: {count}
                    </Badge>
                  ),
                )}
              </HStack>
            </Box>
          </VStack>
        </Box>
      )}
    </VStack>
  );
};
