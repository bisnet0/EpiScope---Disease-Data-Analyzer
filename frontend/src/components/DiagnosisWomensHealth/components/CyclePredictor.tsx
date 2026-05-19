import React, { useState } from "react";
import {
  Box,
  Flex,
  Heading,
  Text,
  Grid,
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
  Divider,
  FormControl,
  FormLabel,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  Center,
  theme,
} from "@chakra-ui/react";
import {
  FaCalendarAlt,
  FaHeartbeat,
  FaSyncAlt,
  FaRegLightbulb,
} from "react-icons/fa";
import { SiGooglefit, SiStrava } from "react-icons/si";

import { useWomensHealthThemeFx } from "../styles/theme-fx";
import { useCyclePredictor } from "../hooks/useCyclePredictor";
import { PiDrop } from "react-icons/pi";

export const CyclePredictor: React.FC = () => {
  const {
    prediction,
    isLoading,
    isUpdating,
    updateProfile,
    refreshPrediction,
  } = useCyclePredictor();
  const themeFx = useWomensHealthThemeFx();

  // Estados locais do formulário de calibração
  const [lastPeriodStart, setLastPeriodStart] = useState("");
  const [cycleLength, setCycleLength] = useState(28);
  const [isPerimenopause, setIsPerimenopause] = useState(false);

  const handleCalibrate = async () => {
    if (!lastPeriodStart) return;
    await updateProfile({
      last_period_start: lastPeriodStart,
      average_cycle_length: cycleLength,
      is_perimenopause: isPerimenopause,
    });
  };

  // Cores dinâmicas baseadas na fase do ciclo
  const getPhaseColor = (phase?: string) => {
    if (!phase) return "gray.400";
    if (phase.includes("Folicular")) return "blue.400";
    if (phase.includes("Fértil")) return "purple.400";
    if (phase.includes("Lútea")) return "orange.400";
    if (phase.includes("Menstruação")) return "red.400";
    return themeFx.textColor;
  };

  return (
    <Box
      p={6}
      bg={themeFx.cardBg}
      border="1px solid"
      borderColor={themeFx.cardBorder}
      borderRadius="2xl"
      backdropFilter="blur(12px)"
      boxShadow="2xl"
      w="full"
    >
      <Flex direction="column" h="full" gap={6} color="white">
        {/* HEADER IGUAL AO DA LAPAROSCOPIA */}
        <Flex
          direction={{ base: "column", sm: "row" }}
          justify="space-between"
          align={{ base: "flex-start", sm: "flex-end" }}
          borderBottom="1px solid"
          borderColor="whiteAlpha.200"
          pb={4}
        >
          <Box>
            <Heading
              size="md"
              letterSpacing="tight"
              color={themeFx.textColor}
              alignItems="center"
              display="flex"
            >
              <Icon as={PiDrop} mr={2} color={themeFx.cicleBg} />
              Ciclo e Perimenopausa
            </Heading>
            <Text fontSize="sm" color={themeFx.mutedText}>
              Previsão de Ciclo e Perimenopausa via Telemetria Cardíaca (RHR)
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
              Fontes Conectadas
            </Text>
            <Flex gap={2}>
              <Badge
                colorScheme="orange"
                variant="subtle"
                px={2}
                py={1}
                borderRadius="md"
                display="flex"
                alignItems="center"
              >
                <Icon as={SiStrava} mr={2} /> Strava
              </Badge>
              <Badge
                colorScheme="blue"
                variant="subtle"
                px={2}
                py={1}
                borderRadius="md"
                display="flex"
                alignItems="center"
              >
                <Icon as={SiGooglefit} mr={2} /> Google Fit
              </Badge>
            </Flex>
          </Box>
        </Flex>

        {/* GRID PRINCIPAL (Esquerda: Inputs | Direita: Output) */}
        <Grid templateColumns={{ base: "1fr", xl: "400px 1fr" }} gap={6}>
          {/* ================= COLUNA ESQUERDA: CALIBRAÇÃO ================= */}
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
              <Flex align="center" justify="space-between" mb={6}>
                <Heading
                  size="sm"
                  color={themeFx.textColor}
                  display="flex"
                  alignItems="center"
                >
                  <Icon as={FaCalendarAlt} mr={2} color="pink.400" />
                  CALIBRAÇÃO DO CICLO
                </Heading>
              </Flex>

              <VStack spacing={5} align="stretch" flex="1">
                <FormControl>
                  <FormLabel fontSize="sm" color={themeFx.mutedText}>
                    Última Menstruação
                  </FormLabel>
                  <Input
                    type="date"
                    value={lastPeriodStart}
                    onChange={(e) => setLastPeriodStart(e.target.value)}
                    bg="blackAlpha.300"
                    border="1px solid"
                    borderColor="whiteAlpha.200"
                    color={themeFx.textColor}
                    _focus={{ borderColor: "pink.400", boxShadow: "none" }}
                    css={{ "color-scheme": "dark" }} // Faz o ícone do calendário ficar escuro
                  />
                </FormControl>

                <FormControl>
                  <FormLabel fontSize="sm" color={themeFx.mutedText}>
                    Duração Média (Dias)
                  </FormLabel>
                  <NumberInput
                    value={cycleLength}
                    onChange={(_, val) => setCycleLength(val || 28)}
                    min={20}
                    max={45}
                    borderColor="whiteAlpha.200"
                  >
                    <NumberInputField
                      bg="blackAlpha.300"
                      color={themeFx.textColor}
                      _focus={{ borderColor: "pink.400" }}
                    />
                    <NumberInputStepper>
                      <NumberIncrementStepper
                        color="whiteAlpha.600"
                        border="none"
                      />
                      <NumberDecrementStepper
                        color="whiteAlpha.600"
                        border="none"
                      />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                <FormControl
                  display="flex"
                  alignItems="center"
                  justifyContent="space-between"
                  p={3}
                  bg="whiteAlpha.50"
                  borderRadius="xl"
                  border="1px solid"
                  borderColor="whiteAlpha.100"
                >
                  <Box>
                    <FormLabel mb="0" fontSize="sm" color={themeFx.textColor}>
                      Perimenopausa
                    </FormLabel>
                    <Text fontSize="xs" color={themeFx.mutedText}>
                      Ativa IA para transição
                    </Text>
                  </Box>
                  <Switch
                    colorScheme="pink"
                    isChecked={isPerimenopause}
                    onChange={(e) => setIsPerimenopause(e.target.checked)}
                  />
                </FormControl>

                <Button
                  mt="auto"
                  colorScheme="pink"
                  size="md"
                  width="full"
                  onClick={handleCalibrate}
                  isLoading={isUpdating}
                  loadingText="Calibrando IA..."
                  isDisabled={!lastPeriodStart}
                  borderRadius="xl"
                >
                  Atualizar Biometria
                </Button>
              </VStack>
            </Box>
          </Flex>

          {/* ================= COLUNA DIREITA: RESULTADOS ================= */}
          <Box h="full" minW={0}>
            {isLoading ? (
              <Center
                h="full"
                minH="300px"
                flexDirection="column"
                border="1px dashed"
                borderColor="whiteAlpha.200"
                borderRadius="2xl"
                bg="blackAlpha.300"
              >
                <Spinner size="xl" color="pink.400" thickness="4px" mb={4} />
                <Text color="gray.400" fontWeight="medium">
                  Sincronizando Wearables...
                </Text>
              </Center>
            ) : prediction && prediction.status !== "pending" ? (
              <Flex direction="column" gap={6} h="full" w="full">
                {/* 1. MÓDULO DE TELEMETRIA CARDÍACA */}
                <Box
                  w="full"
                  bg={themeFx.innerBg}
                  borderRadius="xl"
                  border="1px solid"
                  borderColor={themeFx.cardBorder}
                  p={5}
                >
                  <Flex align="center" justify="space-between" mb={4}>
                    <Heading
                      size="sm"
                      color={themeFx.textColor}
                      display="flex"
                      alignItems="center"
                    >
                      <Icon as={FaHeartbeat} mr={2} color="red.400" />
                      TELEMETRIA DE REPOUSO (RHR)
                    </Heading>
                    <Button
                      size="xs"
                      variant="ghost"
                      colorScheme="blue"
                      leftIcon={<FaSyncAlt />}
                      onClick={refreshPrediction}
                    >
                      Sincronizar
                    </Button>
                  </Flex>

                  <Flex
                    align="center"
                    justify="space-between"
                    p={4}
                    bg="blackAlpha.400"
                    borderRadius="lg"
                    border="1px solid"
                    borderColor="whiteAlpha.100"
                  >
                    <Box>
                      <Text fontSize="sm" color={themeFx.mutedText} mb={1}>
                        Fonte:{" "}
                        {prediction.wearable_telemetry?.source ||
                          "Nenhuma conexão ativa"}
                      </Text>
                      <Flex align="baseline" gap={2}>
                        <Text
                          fontSize="4xl"
                          fontWeight="light"
                          color={
                            prediction.wearable_telemetry?.heart_rate
                              ? "white"
                              : "gray.600"
                          }
                        >
                          {prediction.wearable_telemetry?.heart_rate || "--"}
                        </Text>
                        <Text
                          fontSize="md"
                          color={themeFx.mutedText}
                          fontWeight="medium"
                        >
                          BPM
                        </Text>
                      </Flex>
                    </Box>
                    <Icon
                      as={FaHeartbeat}
                      boxSize={12}
                      color={
                        prediction.wearable_telemetry?.heart_rate
                          ? "red.400"
                          : "gray.600"
                      }
                      opacity={0.5}
                    />
                  </Flex>
                </Box>

                {/* 2. DADOS ESTATÍSTICOS DO CICLO */}
                <Box
                  p={5}
                  bg={themeFx.innerBg}
                  borderRadius="2xl"
                  border="1px solid"
                  borderColor={themeFx.cardBorder}
                >
                  <VStack spacing={5} align="stretch">
                    {/* Insights Médicos (Iterando a lista do Backend) */}
                    {prediction.clinical_insights &&
                      prediction.clinical_insights.map((insight, idx) => (
                        <Alert
                          key={idx}
                          status="info"
                          borderRadius="xl"
                          bg="whiteAlpha.100"
                          color={themeFx.textColor}
                          variant="subtle"
                        >
                          <AlertIcon as={FaRegLightbulb} color="pink.400" />
                          <AlertDescription
                            fontSize="sm"
                            color={themeFx.mutedText}
                          >
                            {insight}
                          </AlertDescription>
                        </Alert>
                      ))}

                    {/* 👇 INTERVENÇÃO DO AGENTE (MAESTRO) */}
                    {prediction.maestro_recommendation && (
                      <Alert
                        status={
                          prediction.maestro_recommendation.includes("ALERTA")
                            ? "error"
                            : "info"
                        }
                        borderRadius="xl"
                        bg={
                          prediction.maestro_recommendation.includes("ALERTA")
                            ? "red.900"
                            : "whiteAlpha.100"
                        }
                        color={
                          prediction.maestro_recommendation.includes("ALERTA")
                            ? "red.100"
                            : themeFx.textColor
                        }
                        variant="subtle"
                        border="1px solid"
                        borderColor={
                          prediction.maestro_recommendation.includes("ALERTA")
                            ? "red.500"
                            : "transparent"
                        }
                      >
                        <AlertIcon
                          color={
                            prediction.maestro_recommendation.includes("ALERTA")
                              ? "red.400"
                              : "blue.400"
                          }
                        />
                        <Box>
                          <AlertTitle
                            fontSize="sm"
                            color={
                              prediction.maestro_recommendation.includes(
                                "ALERTA",
                              )
                                ? "red.300"
                                : "blue.200"
                            }
                          >
                            Diagnóstico do Maestro
                          </AlertTitle>
                          <AlertDescription
                            fontSize="sm"
                            color={
                              prediction.maestro_recommendation.includes(
                                "ALERTA",
                              )
                                ? "red.100"
                                : themeFx.mutedText
                            }
                          >
                            {prediction.maestro_recommendation}
                          </AlertDescription>
                        </Box>
                      </Alert>
                    )}

                    {/* Stats do Ciclo */}
                    <StatGroup mt={2}>
                      <Stat>
                        <StatLabel color={themeFx.mutedText}>
                          Dia do Ciclo
                        </StatLabel>
                        <StatNumber color={themeFx.textColor}>
                          {prediction.current_day_of_cycle}
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel color={themeFx.mutedText}>
                          Fase Estimada
                        </StatLabel>
                        <StatNumber
                          color={getPhaseColor(prediction.estimated_phase)}
                          fontSize="lg"
                          mt={1}
                        >
                          {prediction.estimated_phase}
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel color={themeFx.mutedText}>
                          Próxima Data
                        </StatLabel>
                        <StatNumber
                          color={themeFx.textColor}
                          fontSize="lg"
                          mt={1}
                        >
                          {prediction.next_period_prediction
                            ? new Date(
                                prediction.next_period_prediction,
                              ).toLocaleDateString("pt-BR")
                            : "--"}
                        </StatNumber>
                      </Stat>
                    </StatGroup>
                  </VStack>
                </Box>
              </Flex>
            ) : (
              // ESTADO PENDENTE (Falta Configurar)
              <Center
                h="full"
                minH="300px"
                flexDirection="column"
                border="1px dashed"
                borderColor="whiteAlpha.200"
                bg="blackAlpha.300"
                borderRadius="2xl"
                p={6}
                textAlign="center"
              >
                <Box as={FaCalendarAlt} w={10} h={10} color="gray.600" mb={4} />
                <Heading size="md" color="gray.400">
                  Aguardando Calibração
                </Heading>
                <Text fontSize="sm" color="gray.500" mt={2} maxW="sm">
                  Informe a data da sua última menstruação e a duração média do
                  seu ciclo ao lado para que a IA possa cruzar com sua
                  telemetria cardíaca.
                </Text>
              </Center>
            )}
          </Box>
        </Grid>
      </Flex>
    </Box>
  );
};
