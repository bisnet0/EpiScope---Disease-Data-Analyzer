import React, { useRef } from "react";
import {
  Box,
  Flex,
  Heading,
  Text,
  Grid,
  Center,
  VStack,
  Icon,
  Spinner,
  Button,
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
import {
  FaVideo,
  FaFileVideo,
  FaCheckCircle,
  FaExclamationTriangle,
  FaEye,
} from "react-icons/fa";

import { useWomensHealthThemeFx } from "./styles/theme-fx";
import { useLaparoscopyAnalyzer } from "./hooks/useLaparoscopyAnalyzer";

export const LaparoscopyPage: React.FC = () => {
  // 1. Invoca o nosso hook do YOLO
  const { selectedFile, isAnalyzing, result, handleFileChange, handleAnalyze } =
    useLaparoscopyAnalyzer();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const themeFx = useWomensHealthThemeFx();

  // Função para abrir o seletor de arquivos
  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const bleedingPercentage = result?.bleeding_ratio
    ? (result.bleeding_ratio * 100).toFixed(1)
    : "0.0";

  return (
    <Box
      p={6}
      bg={themeFx.cardBg}
      border="1px solid"
      borderColor={themeFx.cardBorder}
      borderRadius="2xl"
      backdropFilter="blur(12px)"
      boxShadow="2xl"
    >
      <Flex direction="column" h="full" gap={6} color="white">
        {/* HEADER */}
        <Flex
          direction={{ base: "column", sm: "row" }}
          justify="space-between"
          align={{ base: "flex-start", sm: "flex-end" }}
          borderBottom="1px solid"
          borderColor="whiteAlpha.200"
          pb={4}
        >
          <Box>
            <Heading size="md" letterSpacing="tight" color={themeFx.textColor}>
              Análise Cirúrgica
            </Heading>
            <Text fontSize="sm" color={themeFx.mutedText}>
              Detecção de Instrumentos e Risco Hemostático em Laparoscopia
            </Text>
          </Box>

          <Box mt={{ base: 4, sm: 0 }} w={{ base: "full", sm: "auto" }}>
            <Text
              fontSize="xs"
              fontWeight="semibold"
              color={themeFx.mutedText}
              textTransform="uppercase"
              mb={1}
            >
              Procedimento
            </Text>
            <select
              disabled
              className="bg-slate-800 border border-slate-600 text-sm rounded-lg block w-full p-2 outline-none cursor-not-allowed opacity-80"
              style={{
                backgroundColor: "#1a202c",
                color: "white",
                borderColor: "rgba(255,255,255,0.16)",
              }}
            >
              <option value="HISTERECTOMIA">Histerectomia Laparoscópica</option>
            </select>
          </Box>
        </Flex>

        {/* GRID PRINCIPAL (Esquerda: Upload | Direita: Resultados & Frames) */}
        <Grid templateColumns={{ base: "1fr", xl: "400px 1fr" }} gap={6}>
          {/* ================= COLUNA ESQUERDA: INPUTS ================= */}
          {/* ================= COLUNA ESQUERDA: INPUTS ================= */}
          <Flex direction="column" gap={6} h="full">
            <Box
              p={5}
              bg={themeFx.innerBg}
              borderRadius="2xl"
              border="1px solid"
              borderColor={themeFx.cardBorder}
              h="full"
              display="flex"
              flexDirection="column"
            >
              <Flex align="center" justify="space-between" mb={4}>
                <Heading
                  size="sm"
                  color={themeFx.textColor}
                  display="flex"
                  alignItems="center"
                >
                  <Icon as={FaVideo} mr={2} color="blue.400" />
                  ENTRADA DE VÍDEO
                </Heading>
              </Flex>

              <VStack spacing={4} align="stretch" flex="1">
                {/* DROPZONE */}
                <Center
                  flex="1"
                  w="full"
                  minH="200px"
                  p={6}
                  flexDirection="column"
                  border="2px dashed"
                  borderColor={selectedFile ? "blue.400" : themeFx.cardBorder}
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
                        color={themeFx.textColor}
                        textAlign="center"
                        noOfLines={1}
                      >
                        {selectedFile.name}
                      </Text>
                      <Text fontSize="sm" color={themeFx.mutedText}>
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </Text>
                    </VStack>
                  ) : (
                    <VStack spacing={2}>
                      <Icon
                        as={FaFileVideo}
                        fontSize="3xl"
                        color={themeFx.mutedText}
                      />
                      <Text
                        color={themeFx.mutedText}
                        textAlign="center"
                        fontSize="sm"
                      >
                        Selecione o vídeo da cirurgia
                      </Text>
                    </VStack>
                  )}
                </Center>

                {/* BOTÃO / SPINNER */}
                {isAnalyzing ? (
                  <Flex align="center" justify="center" p={2} color="blue.400">
                    <Spinner size="sm" mr={3} />
                    <Text fontSize="sm" fontWeight="bold">
                      YOLOv8 Extraindo Frames...
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
                    {result
                      ? "Reanalisar Vídeo"
                      : "Iniciar Visão Computacional"}
                  </Button>
                )}
              </VStack>
            </Box>
          </Flex>

          {/* ================= COLUNA DIREITA: OUTPUT E FRAMES ================= */}
          <Box h="full" minW={0}>
            {result && result.status === "success" ? (
              <Flex direction="column" gap={6} h="full" w="full">
                {/* 1. MÓDULO DE AUDITORIA VISUAL (Frames do YOLOv8) */}
                <Box
                  w="full"
                  bg={themeFx.innerBg}
                  borderRadius="xl"
                  border="1px solid"
                  borderColor={themeFx.cardBorder}
                  p={4}
                >
                  <Flex align="center" justify="space-between" mb={3}>
                    <Heading
                      size="sm"
                      color={themeFx.textColor}
                      display="flex"
                      alignItems="center"
                    >
                      <Icon as={FaEye} mr={2} color="blue.400" />
                      AUDITORIA VISUAL (FRAMES EXTRAÍDOS)
                    </Heading>
                    <Badge colorScheme="blue" variant="subtle">
                      {result.annotated_frames?.length || 0} Capturas
                    </Badge>
                  </Flex>

                  {result.annotated_frames &&
                  result.annotated_frames.length > 0 ? (
                    <Box
                      w="full"
                      overflowX="auto"
                      pb={2}
                      sx={{
                        "&::-webkit-scrollbar": { height: "8px" },
                        "&::-webkit-scrollbar-track": {
                          background: "rgba(255,255,255,0.05)",
                          borderRadius: "4px",
                        },
                        "&::-webkit-scrollbar-thumb": {
                          background: "rgba(255,255,255,0.2)",
                          borderRadius: "4px",
                        },
                      }}
                    >
                      {/* Flex com max-content e itens com flexShrink=0 garantem o scroll perfeito */}
                      <Flex gap={4} w="max-content">
                        {result.annotated_frames.map((b64Img, index) => (
                          <Box
                            key={index}
                            flexShrink={0}
                            w="280px"
                            h="180px"
                            borderRadius="lg"
                            overflow="hidden"
                            border="1px solid"
                            borderColor="whiteAlpha.300"
                            boxShadow="sm"
                            position="relative"
                          >
                            <img
                              src={b64Img}
                              alt={`Frame detectado ${index + 1}`}
                              style={{
                                width: "100%",
                                height: "100%",
                                objectFit: "cover",
                              }}
                            />
                            <Badge
                              position="absolute"
                              bottom={2}
                              right={2}
                              colorScheme="blackAlpha"
                              bg="blackAlpha.800"
                              fontSize="2xs"
                            >
                              Frame #{index + 1}
                            </Badge>
                          </Box>
                        ))}
                      </Flex>
                    </Box>
                  ) : (
                    <Center
                      h="150px"
                      flexDirection="column"
                      border="1px dashed"
                      borderColor="whiteAlpha.200"
                      borderRadius="md"
                    >
                      <Icon as={FaEye} boxSize={6} color="gray.600" mb={2} />
                      <Text fontSize="sm" color="gray.500">
                        Nenhum instrumento detectado na amostra de vídeo.
                      </Text>
                    </Center>
                  )}
                </Box>

                {/* 2. DADOS ESTATÍSTICOS DA CIRURGIA */}
                <Box
                  p={5}
                  bg={themeFx.innerBg}
                  borderRadius="2xl"
                  border="1px solid"
                  borderColor={themeFx.cardBorder}
                >
                  <VStack spacing={5} align="stretch">
                    {/* Alertas */}
                    {result.clinical_alerts &&
                      result.clinical_alerts.length > 0 && (
                        <Alert
                          status="error"
                          borderRadius="xl"
                          bg="red.900"
                          color="red.100"
                        >
                          <AlertIcon
                            as={FaExclamationTriangle}
                            color="red.300"
                          />
                          <AlertDescription fontSize="sm" fontWeight="medium">
                            {result.clinical_alerts[0]}
                          </AlertDescription>
                        </Alert>
                      )}

                    <Alert
                      status="info"
                      borderRadius="xl"
                      bg="whiteAlpha.100"
                      color={themeFx.textColor}
                      variant="subtle"
                    >
                      <AlertIcon color="blue.400" />
                      <Box>
                        <AlertTitle fontSize="sm" color="blue.200">
                          Recomendação do Maestro
                        </AlertTitle>
                        <AlertDescription
                          fontSize="sm"
                          color={themeFx.mutedText}
                        >
                          {result.maestro_recommendation}
                        </AlertDescription>
                      </Box>
                    </Alert>

                    {/* Estatísticas */}
                    <StatGroup>
                      <Stat>
                        <StatLabel color={themeFx.mutedText}>Tempo</StatLabel>
                        <StatNumber color={themeFx.textColor}>
                          {result.total_analyzed_seconds}s
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel color={themeFx.mutedText}>
                          Hemostasia
                        </StatLabel>
                        <StatNumber
                          color={
                            Number(bleedingPercentage) > 20
                              ? "red.400"
                              : "green.400"
                          }
                        >
                          {bleedingPercentage}%
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel color={themeFx.mutedText}>
                          Itens Encontrados
                        </StatLabel>
                        <StatNumber color={themeFx.textColor}>
                          {Object.keys(result.items_detected || {}).length}
                        </StatNumber>
                      </Stat>
                    </StatGroup>

                    <Divider borderColor={themeFx.cardBorder} />

                    <Box>
                      <Text
                        fontWeight="semibold"
                        color={themeFx.mutedText}
                        mb={3}
                        fontSize="sm"
                      >
                        Telemetria Detalhada (Frames)
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
              </Flex>
            ) : (
              // ESTADO VAZIO (Aguardando Vídeo)
              <Flex
                direction="column"
                align="center"
                justify="center"
                h="full"
                minH="300px"
                border="1px solid"
                borderColor="whiteAlpha.200"
                bg="blackAlpha.300"
                borderRadius="xl"
                p={6}
                textAlign="center"
              >
                <Box as={FaVideo} w={10} h={10} color="gray.600" mb={4} />
                <Heading size="md" color="gray.400">
                  Aguardando Vídeo Cirúrgico
                </Heading>
                <Text fontSize="sm" color="gray.500" mt={2} maxW="sm">
                  Faça o upload do vídeo da laparoscopia para que o modelo de
                  Inteligência Artificial mapeie os instrumentos e classifique o
                  risco do procedimento.
                </Text>
              </Flex>
            )}
          </Box>
        </Grid>
      </Flex>
    </Box>
  );
};
