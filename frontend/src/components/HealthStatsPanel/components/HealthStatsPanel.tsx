import React from "react";
import {
  Box,
  Flex,
  Text,
  Button,
  Heading,
  Icon,
  SimpleGrid,
  Badge,
  Spinner,
  Center,
  VStack,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  Table,
  Tbody,
  Tr,
  Td,
  Progress,
  HStack,
  Stack,
} from "@chakra-ui/react";
import {
  FaStrava,
  FaHeartbeat,
  FaRunning,
  FaSync,
  FaClock,
  FaCalendarAlt,
  FaGoogle,
  FaLink,
} from "react-icons/fa";
import { useHealthStats } from "../hooks/useHealthStats";
import { useHealthStatsThemeFx } from "../styles/theme-fx";

const HealthStatsPanel: React.FC = () => {
  // Adicione isConnectedGoogle e handleConnectGoogle no seu useHealthStats hook depois
  const {
    isConnected,
    loading,
    handleConnect,
    activities,
    handleSync,
    isSyncing,
    isConnectedGoogle,
    handleConnectGoogle,
    googleMetrics,
  } = useHealthStats();

  const theme = useHealthStatsThemeFx();
  const sleepMinutes = googleMetrics?.sleep_minutes || 0;

  const lastActivity = activities.length > 0 ? activities[0] : null;
  const weeklyMinutes = activities
    .slice(0, 7)
    .reduce((acc, curr) => acc + curr.moving_time_min, 0);
  const targetMinutes = 300;
  const progress = (weeklyMinutes / targetMinutes) * 100;

  if (loading)
    return (
      <Center p={20}>
        <Spinner color="cyan.400" size="xl" />
      </Center>
    );

  return (
    <Box
      p={6}
      bg={theme.cardBg}
      border="1px solid"
      borderColor={theme.cardBorder}
      borderRadius="2xl"
      backdropFilter="blur(12px)"
      boxShadow="2xl"
    >
      {/* HEADER DINÂMICO */}
      <Flex
        align="center"
        justify="space-between"
        mb={8}
        direction={{ base: "column", md: "row" }}
        gap={4}
      >
        <VStack align="start" spacing={0}>
          <Heading
            size="md"
            color={theme.textColor}
            display="flex"
            alignItems="center"
          >
            <Icon as={FaRunning} mr={3} color="cyan.400" />
            Central de Saúde
          </Heading>
          <Text fontSize="md" color={theme.mutedText}>
            {isConnected
              ? `Sincronização com ${activities.length} atividades`
              : "Conecte seus dispositivos para começar"}
          </Text>
        </VStack>

        <HStack spacing={3}>
          {isConnected && (
            <Button
              leftIcon={<FaSync />}
              size="sm"
              variant="ghost"
              color="cyan.400"
              onClick={handleSync}
              isLoading={isSyncing}
            >
              Sincronizar
            </Button>
          )}

          {/* Botão Strava Dinâmico */}
          {!isConnected ? (
            <Button
              leftIcon={<FaStrava />}
              colorScheme="orange"
              onClick={handleConnect}
              size="md"
            >
              Conectar Strava
            </Button>
          ) : (
            <Badge colorScheme="green" variant="subtle" p={2} borderRadius="lg">
              STRAVA ON
            </Badge>
          )}

          {/* Botão Google Fit (Novo!) */}
          {!isConnectedGoogle ? (
            <Button
              leftIcon={<FaGoogle />}
              variant="outline"
              borderColor="whiteAlpha.300"
              color="white"
              _hover={{ bg: "whiteAlpha.100" }}
              onClick={handleConnectGoogle}
              size="md"
            >
              Google Fit
            </Button>
          ) : (
            <Badge
              colorScheme="blue"
              variant="subtle"
              p={2}
              borderRadius="lg"
              display="flex"
              alignItems="center"
            >
              <Icon as={FaGoogle} mr={1} /> GOOGLE ON
            </Badge>
          )}
        </HStack>
      </Flex>

      {/* Se não houver atividades e não estiver conectado, mostra um Empty State chamativo */}
      {!isConnected && activities.length === 0 ? (
        <Center
          p={10}
          flexDirection="column"
          bg="whiteAlpha.50"
          borderRadius="xl"
          border="1px dashed"
          borderColor="whiteAlpha.300"
        >
          <Icon as={FaLink} fontSize="4xl" color="cyan.400" mb={4} />
          <Text fontWeight="bold" color="white" mb={2}>
            Nenhuma conta de saúde vinculada
          </Text>
          <Text color={theme.mutedText} textAlign="center" maxW="md">
            Vincule seu Strava para importar treinos e o Google Fit para
            monitorar sono e passos. O Dr. EpiScope usará esses dados para
            diagnósticos precisos.
          </Text>
        </Center>
      ) : (
        <>
          <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6} mb={8}>
            {/* CARD 1: CARGA SEMANAL */}
            <Box
              p={5}
              bg={theme.innerBg}
              borderRadius="2xl"
              border="1px solid"
              borderColor={theme.cardBorder}
            >
              <Text
                color={theme.mutedText}
                fontSize="sm"
                fontWeight="bold"
                mb={4}
                display="flex"
                alignItems="center"
              >
                <Icon as={FaClock} mr={2} color="orange.400" /> CARGA SEMANAL
              </Text>
              <Stat>
                <StatNumber color={theme.textColor} fontSize="4xl">
                  {Math.round(weeklyMinutes)}{" "}
                  <Text as="span" fontSize="lg">
                    min
                  </Text>
                </StatNumber>
                <StatHelpText color={theme.mutedText}>
                  Meta: {targetMinutes} min/semana
                </StatHelpText>
              </Stat>
              <Progress
                value={progress}
                size="sm"
                colorScheme="orange"
                borderRadius="full"
                mt={4}
                bg="whiteAlpha.100"
              />
            </Box>

            {/* CARD 2: ÚLTIMO ESFORÇO */}
            <Box
              p={5}
              bg={theme.innerBg}
              borderRadius="2xl"
              border="1px solid"
              borderColor={theme.cardBorder}
            >
              <Text
                color={theme.mutedText}
                fontSize="sm"
                fontWeight="bold"
                mb={4}
                display="flex"
                alignItems="center"
              >
                <Icon as={FaRunning} mr={2} color="cyan.400" /> ÚLTIMO ESFORÇO
              </Text>
              {lastActivity ? (
                <Stat>
                  <StatLabel
                    color={theme.textColor}
                    fontSize="lg"
                    noOfLines={1}
                  >
                    {lastActivity.name}
                  </StatLabel>
                  <StatNumber color="cyan.400" fontSize="4xl">
                    {lastActivity.distance_km > 0
                      ? `${lastActivity.distance_km} KM`
                      : `${lastActivity.moving_time_min} MIN`}
                  </StatNumber>
                  <Badge variant="subtle" colorScheme="cyan">
                    {lastActivity.type}
                  </Badge>
                </Stat>
              ) : (
                <Text color={theme.mutedText}>Aguardando dados...</Text>
              )}
            </Box>

            {/* CARD 3: STATUS CARDIO */}
            <Box
              p={5}
              bg={theme.innerBg}
              borderRadius="2xl"
              border="1px solid"
              borderColor={theme.cardBorder}
            >
              <Text
                color={theme.mutedText}
                fontSize="sm"
                fontWeight="bold"
                mb={4}
                display="flex"
                alignItems="center"
              >
                <Icon as={FaHeartbeat} mr={2} color="red.400" /> STATUS CARDIO
              </Text>
              {lastActivity?.avg_hr ? (
                <Stat>
                  <StatNumber color="red.400" fontSize="4xl">
                    {Math.round(lastActivity.avg_hr)}{" "}
                    <Text as="span" fontSize="lg">
                      BPM
                    </Text>
                  </StatNumber>
                  <StatHelpText>Média registrada via sensor</StatHelpText>
                </Stat>
              ) : (
                <VStack align="start" spacing={1}>
                  <Text fontSize="sm" color="orange.300" fontWeight="bold">
                    Sem sensor cardíaco
                  </Text>
                  <Text fontSize="xs" color={theme.mutedText}>
                    Conecte um wearable para ver batimentos.
                  </Text>
                </VStack>
              )}
            </Box>
            <Box
              p={5}
              bg={theme.innerBg}
              borderRadius="2xl"
              border="1px solid"
              borderColor={theme.cardBorder}
            >
              <Text
                color={theme.mutedText}
                fontSize="sm"
                fontWeight="bold"
                mb={4}
                display="flex"
                alignItems="center"
              >
                <Icon as={FaClock} mr={2} color="purple.400" /> RECUPERAÇÃO
                (SONO)
              </Text>
              <Stat>
                {isConnectedGoogle ? (
                  <>
                    <StatNumber color="purple.300" fontSize="4xl">
                      {Math.floor(sleepMinutes / 60)}h {sleepMinutes % 60}m
                    </StatNumber>
                    <StatHelpText>Sincronizado via Google Fit</StatHelpText>
                  </>
                ) : (
                  <Text fontSize="xs" color={theme.mutedText}>
                    Conecte o Google Fit para monitorar o sono.
                  </Text>
                )}
              </Stat>
            </Box>

            {/* CARD 5: ATIVIDADE DIÁRIA (PASSOS) */}
            {isConnectedGoogle && (
              <Box
                p={5}
                bg={theme.innerBg}
                borderRadius="2xl"
                border="1px solid"
                borderColor={theme.cardBorder}
              >
                <Text
                  color={theme.mutedText}
                  fontSize="sm"
                  fontWeight="bold"
                  mb={4}
                  display="flex"
                  alignItems="center"
                >
                  <Icon as={FaRunning} mr={2} color="green.400" /> PASSOS (HOJE)
                </Text>
                <Stat>
                  <StatNumber color="green.300" fontSize="4xl">
                    {googleMetrics.steps.toLocaleString("pt-BR")}
                  </StatNumber>
                  <StatHelpText color={theme.mutedText}>
                    Meta: 10.000 passos
                  </StatHelpText>
                </Stat>
                <Progress
                  value={(googleMetrics.steps / 10000) * 100}
                  size="sm"
                  colorScheme="green"
                  borderRadius="full"
                  mt={4}
                  bg="whiteAlpha.100"
                />
              </Box>
            )}

            {/* CARD 6: CARDIO REPOUSO (BPM MÍN) */}
            {isConnectedGoogle && googleMetrics.bpm_min > 0 && (
              <Box
                p={5}
                bg={theme.innerBg}
                borderRadius="2xl"
                border="1px solid"
                borderColor={theme.cardBorder}
              >
                <Text
                  color={theme.mutedText}
                  fontSize="sm"
                  fontWeight="bold"
                  mb={4}
                  display="flex"
                  alignItems="center"
                >
                  <Icon as={FaHeartbeat} mr={2} color="pink.400" /> BPM REPOUSO
                </Text>
                <Stat>
                  <StatNumber color="pink.300" fontSize="4xl">
                    {Math.round(googleMetrics.bpm_min)}{" "}
                    <Text as="span" fontSize="lg">
                      BPM
                    </Text>
                  </StatNumber>
                  <StatHelpText color={theme.mutedText}>
                    Mínimo detectado hoje
                  </StatHelpText>
                </Stat>
                <Text
                  fontSize="xs"
                  mt={4}
                  color={
                    googleMetrics.bpm_min < 70 ? "green.300" : "orange.300"
                  }
                >
                  {googleMetrics.bpm_min < 70
                    ? "● Coração em modo recuperação"
                    : "● Batimento basal elevado"}
                </Text>
              </Box>
            )}
          </SimpleGrid>

          {/* TABELA DE HISTÓRICO */}
          <Box mt={10}>
            <Heading
              size="sm"
              color={theme.textColor}
              mb={6}
              display="flex"
              alignItems="center"
            >
              <Icon as={FaCalendarAlt} mr={2} /> LOG DE ATIVIDADES RECENTES
            </Heading>
            <Box
              overflowX="auto"
              bg="blackAlpha.300"
              borderRadius="xl"
              border="1px solid"
              borderColor={theme.cardBorder}
            >
              <Table variant="simple" size="sm">
                <Tbody>
                  {activities.map((act) => (
                    <Tr
                      key={act.id}
                      _hover={{ bg: "whiteAlpha.50" }}
                      transition="0.2s"
                    >
                      <Td borderColor={theme.cardBorder} py={4}>
                        <Text fontWeight="bold" color={theme.textColor}>
                          {act.name}
                        </Text>
                        <Text fontSize="xs" color={theme.mutedText}>
                          {new Date(act.date).toLocaleDateString()}
                        </Text>
                      </Td>
                      <Td borderColor={theme.cardBorder}>
                        <Badge variant="outline" colorScheme="cyan">
                          {act.type}
                        </Badge>
                      </Td>
                      <Td borderColor={theme.cardBorder} textAlign="right">
                        <Text fontWeight="bold" color="cyan.300">
                          {act.distance_km > 0
                            ? `${act.distance_km} km`
                            : `${act.moving_time_min} min`}
                        </Text>
                      </Td>
                      <Td borderColor={theme.cardBorder} textAlign="right">
                        <Icon
                          as={FaHeartbeat}
                          color={act.avg_hr ? "red.400" : "gray.600"}
                          mr={1}
                        />
                        <Text
                          as="span"
                          fontSize="xs"
                          color={act.avg_hr ? theme.textColor : "gray.600"}
                        >
                          {act.avg_hr ? `${Math.round(act.avg_hr)} bpm` : "--"}
                        </Text>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          </Box>
        </>
      )}
    </Box>
  );
};

export default HealthStatsPanel;
