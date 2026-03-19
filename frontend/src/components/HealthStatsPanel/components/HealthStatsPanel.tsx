import React from 'react';
import { 
  Box, Flex, Text, Button, Heading, Icon, SimpleGrid, Badge, Spinner, 
  Center, VStack, Stat, StatLabel, StatNumber, StatHelpText, Divider, 
  Table, Tbody, Tr, Td, Progress 
} from '@chakra-ui/react';
import { FaStrava, FaHeartbeat, FaRunning, FaSync, FaClock, FaCalendarAlt } from 'react-icons/fa';
import { useHealthStats } from '../hooks/useHealthStats';
import { useHealthStatsThemeFx } from '../styles/theme-fx';

const HealthStatsPanel: React.FC = () => {
  const { isConnected, loading, handleConnect, activities, handleSync, isSyncing } = useHealthStats();
  const theme = useHealthStatsThemeFx();

  const lastActivity = activities.length > 0 ? activities[0] : null;

  // Cálculo de Carga Semanal (Soma dos minutos dos últimos 7 dias)
  const weeklyMinutes = activities.slice(0, 7).reduce((acc, curr) => acc + curr.moving_time_min, 0);
  const targetMinutes = 300; // Meta de 5h por semana
  const progress = (weeklyMinutes / targetMinutes) * 100;

  if (loading) return <Center p={20}><Spinner color="cyan.400" size="xl" /></Center>;

  return (
    <Box p={6} bg={theme.cardBg} border="1px solid" borderColor={theme.cardBorder} borderRadius="2xl" backdropFilter="blur(12px)" boxShadow="2xl">
      
      {/* HEADER DINÂMICO */}
      <Flex align="center" justify="space-between" mb={8} direction={{ base: 'column', md: 'row' }} gap={4}>
        <VStack align="start" spacing={0}>
          <Heading size="lg" color={theme.textColor} display="flex" alignItems="center">
            <Icon as={FaRunning} mr={3} color="cyan.400" /> HealthStats Hub
          </Heading>
          <Text fontSize="md" color={theme.mutedText}>Sincronização com {activities.length} atividades processadas</Text>
        </VStack>

        <Flex gap={3}>
          <Button leftIcon={<FaSync />} size="md" variant="solid" colorScheme="cyan" onClick={handleSync} isLoading={isSyncing}>
            Sincronizar Agora
          </Button>
          <Badge colorScheme="green" variant="outline" p={3} borderRadius="xl" fontSize="xs">
            CONECTADO AO STRAVA
          </Badge>
        </Flex>
      </Flex>

      <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6} mb={8}>
        
        {/* CARD 1: CARGA SEMANAL */}
        <Box p={5} bg={theme.innerBg} borderRadius="2xl" border="1px solid" borderColor={theme.cardBorder}>
          <Text color={theme.mutedText} fontSize="sm" fontWeight="bold" mb={4} display="flex" alignItems="center">
            <Icon as={FaClock} mr={2} color="orange.400" /> CARGA SEMANAL
          </Text>
          <Stat>
            <StatNumber color={theme.textColor} fontSize="4xl">{Math.round(weeklyMinutes)} <Text as="span" fontSize="lg">min</Text></StatNumber>
            <StatHelpText color={theme.mutedText}>Meta: {targetMinutes} min/semana</StatHelpText>
          </Stat>
          <Progress value={progress} size="sm" colorScheme="orange" borderRadius="full" mt={4} bg="whiteAlpha.100" />
        </Box>

        {/* CARD 2: ÚLTIMO TREINO (TRATANDO 0 KM) */}
        <Box p={5} bg={theme.innerBg} borderRadius="2xl" border="1px solid" borderColor={theme.cardBorder}>
          <Text color={theme.mutedText} fontSize="sm" fontWeight="bold" mb={4} display="flex" alignItems="center">
            <Icon as={FaRunning} mr={2} color="cyan.400" /> ÚLTIMO ESFORÇO
          </Text>
          {lastActivity && (
            <Stat>
              <StatLabel color={theme.textColor} fontSize="lg" noOfLines={1}>{lastActivity.name}</StatLabel>
              <StatNumber color="cyan.400" fontSize="4xl">
                {lastActivity.distance_km > 0 ? `${lastActivity.distance_km} KM` : `${lastActivity.moving_time_min} MIN`}
              </StatNumber>
              <Badge variant="subtle" colorScheme="cyan">{lastActivity.type}</Badge>
            </Stat>
          )}
        </Box>

        {/* CARD 3: STATUS CARDIO */}
        <Box p={5} bg={theme.innerBg} borderRadius="2xl" border="1px solid" borderColor={theme.cardBorder}>
          <Text color={theme.mutedText} fontSize="sm" fontWeight="bold" mb={4} display="flex" alignItems="center">
            <Icon as={FaHeartbeat} mr={2} color="red.400" /> STATUS CARDIO
          </Text>
          {lastActivity?.avg_hr ? (
            <Stat>
              <StatNumber color="red.400" fontSize="4xl">{Math.round(lastActivity.avg_hr)} <Text as="span" fontSize="lg">BPM</Text></StatNumber>
              <StatHelpText>Média registrada via sensor</StatHelpText>
            </Stat>
          ) : (
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="orange.300" fontWeight="bold">Sem sensor cardíaco</Text>
              <Text fontSize="xs" color={theme.mutedText}>Os treinos recentes não possuem dados de BPM para análise de intensidade.</Text>
            </VStack>
          )}
        </Box>
      </SimpleGrid>

      {/* TABELA DE HISTÓRICO COMPLETA */}
      <Box mt={10}>
        <Heading size="sm" color={theme.textColor} mb={6} display="flex" alignItems="center">
           <Icon as={FaCalendarAlt} mr={2} /> LOG DE ATIVIDADES RECENTES
        </Heading>
        <Box overflowX="auto" bg="blackAlpha.300" borderRadius="xl" border="1px solid" borderColor={theme.cardBorder}>
          <Table variant="simple" size="sm">
            <Tbody>
              {activities.map((act) => (
                <Tr key={act.id} _hover={{ bg: "whiteAlpha.50" }} transition="0.2s">
                  <Td borderColor={theme.cardBorder} py={4}>
                    <Text fontWeight="bold" color={theme.textColor}>{act.name}</Text>
                    <Text fontSize="xs" color={theme.mutedText}>{new Date(act.date).toLocaleDateString()}</Text>
                  </Td>
                  <Td borderColor={theme.cardBorder}>
                    <Badge variant="outline" colorScheme="cyan">{act.type}</Badge>
                  </Td>
                  <Td borderColor={theme.cardBorder} textAlign="right">
                    <Text fontWeight="bold" color="cyan.300">
                      {act.distance_km > 0 ? `${act.distance_km} km` : `${act.moving_time_min} min`}
                    </Text>
                  </Td>
                  <Td borderColor={theme.cardBorder} textAlign="right">
                    <Icon as={FaHeartbeat} color={act.avg_hr ? "red.400" : "gray.600"} mr={1} />
                    <Text as="span" fontSize="xs" color={act.avg_hr ? theme.textColor : "gray.600"}>
                      {act.avg_hr ? `${Math.round(act.avg_hr)} bpm` : '--'}
                    </Text>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </Box>
    </Box>
  );
};

export default HealthStatsPanel;