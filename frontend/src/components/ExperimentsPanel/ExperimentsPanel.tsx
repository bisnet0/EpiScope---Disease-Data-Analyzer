import React from 'react';
import { Box, Flex, Heading, Text, Badge } from '@chakra-ui/react';
import { useExperiments } from './hooks/useExperiments';
import { ControlsColumn } from './components/ControlsColumn';
import { ChartsColumn } from './components/ChartsColumn';
import { useExperimentsThemeFx } from './styles/theme-fx';
import Toast from '../Toast/Toast';

export const ExperimentsPanel: React.FC = () => {
  const { state, setters, actions } = useExperiments();
  const themeFx = useExperimentsThemeFx();

  return (
    <Box mt={10} borderTop="1px solid" borderColor={themeFx.cardBorder} pt={8}>
      
      <Heading size="md" display="flex" alignItems="center" gap={3} color={themeFx.textColor} mb={2}>
        🧪 Laboratório de Hiperparâmetros 
        <Badge colorScheme="purple" variant="solid" borderRadius="md" px={2} py={0.5}>
          MODO AVANÇADO
        </Badge>
      </Heading>

      <Text color={themeFx.mutedText} fontSize="md" mb={6}>
        Utilize Algoritmos Genéticos para encontrar a configuração perfeita ou teste manualmente.
      </Text>

      <Flex gap={6} flexWrap="wrap">
        <ControlsColumn state={state} setters={setters} actions={actions} />
        
        <ChartsColumn 
          viewMode={state.viewMode} 
          setViewMode={setters.setViewMode}
          manualHistory={state.manualHistory}
          evolutionHistory={state.evolutionHistory}
        />
      </Flex>

      {state.toast && (
        <Toast 
          type={state.toast.type} 
          message={state.toast.message} 
          onClose={setters.closeToast} 
          title={state.toast.title} 
        />
      )}
    </Box>
  );
};