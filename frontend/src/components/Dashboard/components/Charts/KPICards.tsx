import { SimpleGrid, Box, Flex, Text, Icon } from "@chakra-ui/react";
import { ClipboardData, Trophy, Cpu } from "react-bootstrap-icons";
import { useDashboardThemeFx } from "../../styles/theme-fx";

const StatCard = ({ title, value, icon, color, sub, themeFx }: any) => (
  <Box
    bg={themeFx.cardBg}
    p={6}
    borderRadius="xl"
    border="1px solid"
    borderColor={themeFx.cardBorder}
    borderLeft={`4px solid ${color}`}
    boxShadow="lg"
    backdropFilter="blur(16px)"
    transition="transform 0.2s"
    _hover={{ transform: 'translateY(-2px)' }}
  >
    <Flex justify="space-between" align="start" mb={3}>
      <Text color={themeFx.mutedText} fontSize="xs" fontWeight="bold" textTransform="uppercase" letterSpacing="wide">
        {title}
      </Text>
      <Box color={color}>{icon}</Box>
    </Flex>
    <Text fontSize="3xl" fontWeight="black" color={themeFx.textColor} lineHeight="1">
      {value}
    </Text>
    {sub && (
      <Text fontSize="xs" color={themeFx.mutedText} mt={2} fontWeight="medium">
        {sub}
      </Text>
    )}
  </Box>
);

export const KPICards = ({ kpis }: { kpis: any }) => {
  const themeFx = useDashboardThemeFx();

  return (
    <SimpleGrid columns={{ base: 1, sm: 2, lg: 4 }} spacing={6} mb={8}>
      <StatCard themeFx={themeFx} title="Diagnósticos (Filtrado)" value={kpis.total_diagnoses} icon={<Icon as={ClipboardData} boxSize={6} />} color="#3498db" />
      <StatCard themeFx={themeFx} title="Melhor Acurácia" value={`${kpis.best_ai_accuracy}%`} icon={<Icon as={Trophy} boxSize={6} />} color="#f1c40f" />
      <StatCard themeFx={themeFx} title="Treinamentos Realizados" value={kpis.total_trainings} icon={<Icon as={Cpu} boxSize={6} />} color="#9b59b6" />
      <StatCard themeFx={themeFx} title="Status Blockchain" value="Ativo" sub="Consenso Local" color="#2ecc71"
        icon={<Box w="12px" h="12px" bg="#2ecc71" borderRadius="full" boxShadow="0 0 8px #2ecc71" mt={1} />}
      />
    </SimpleGrid>
  );
};