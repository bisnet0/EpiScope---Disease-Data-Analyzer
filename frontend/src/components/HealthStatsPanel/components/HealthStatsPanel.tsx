import React from 'react';
import { 
  Box, Flex, Text, Button, Heading, Icon, 
  SimpleGrid, Badge, Spinner, Center, VStack 
} from '@chakra-ui/react';
import { FaStrava, FaHeartbeat, FaRunning, FaLink } from 'react-icons/fa';
import { useHealthStats } from '../hooks/useHealthStats';
import { useHealthStatsThemeFx } from '../styles/theme-fx';

const HealthStatsPanel: React.FC = () => {
  const { isConnected, loading, handleConnect } = useHealthStats();
  const theme = useHealthStatsThemeFx();

  return (
    <Box
      p={6}
      bg={theme.cardBg}
      border="1px solid"
      borderColor={theme.cardBorder}
      borderRadius="2xl"
      backdropFilter="blur(12px)"
      boxShadow="xl"
    >
      <Flex align="center" justify="space-between" mb={8}>
        <VStack align="start" spacing={0}>
          <Heading size="md" color={theme.textColor} display="flex" alignItems="center">
            <Icon as={FaRunning} mr={2} color="cyan.400" /> HealthStats Hub
          </Heading>
          <Text fontSize="sm" color={theme.mutedText}>
            Sincronização Fisiológica & Wearables
          </Text>
        </VStack>

        {isConnected ? (
          <Badge colorScheme="green" variant="subtle" p={2} borderRadius="lg" display="flex" alignItems="center">
            <Icon as={FaStrava} mr={1} /> Conectado
          </Badge>
        ) : (
          <Button
            leftIcon={<FaLink />}
            bg={theme.accentColor}
            color="white"
            _hover={{ opacity: 0.9, transform: 'translateY(-2px)' }}
            onClick={handleConnect}
            isLoading={loading}
          >
            Conectar Strava
          </Button>
        )}
      </Flex>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        {/* Métricas Cardíacas */}
        <Box p={4} bg={theme.innerBg} borderRadius="xl" border="1px solid" borderColor={theme.cardBorder}>
          <Flex align="center" mb={3}>
            <Center p={2} bg="red.500/10" borderRadius="lg" mr={3}>
              <Icon as={FaHeartbeat} color="red.400" />
            </Center>
            <Text fontWeight="bold" color={theme.textColor}>Cardio Report</Text>
          </Flex>
          <Text fontSize="xs" color={theme.mutedText}>
            {isConnected ? "Aguardando sincronização de BPM..." : "Conecte sua conta para importar batimentos."}
          </Text>
        </Box>

        {/* Atividades Recentes */}
        <Box p={4} bg={theme.innerBg} borderRadius="xl" border="1px solid" borderColor={theme.cardBorder}>
          <Flex align="center" mb={3}>
            <Center p={2} bg="cyan.500/10" borderRadius="lg" mr={3}>
              <Icon as={FaStrava} color="cyan.400" />
            </Center>
            <Text fontWeight="bold" color={theme.textColor}>Atividades Recentes</Text>
          </Flex>
          <Text fontSize="xs" color={theme.mutedText}>
            {isConnected ? "Mapeando volume de treino..." : "Dados de performance indisponíveis."}
          </Text>
        </Box>
      </SimpleGrid>
    </Box>
  );
};

export default HealthStatsPanel;