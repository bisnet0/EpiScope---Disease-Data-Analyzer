import React from 'react';
import { Box, Flex, Heading, Text, Badge } from '@chakra-ui/react';
import { useGlaucomaExperiments } from './hooks/useGlaucomaExperiments';
import { GlaucomaControls } from './components/GlaucomaControls';
import { GlaucomaEvolutionChart } from './components/GlaucomaEvolutionChart';
import { useGlaucomaExpThemeFx } from './styles/theme-fx';
import Toast from '../Toast/Toast'; 


export const GlaucomaExperimentsPanel: React.FC = () => {
  const { state, setters, actions } = useGlaucomaExperiments();
  const themeFx = useGlaucomaExpThemeFx();

  return (
    <Box mt={10} borderTop="1px solid" borderColor={themeFx.cardBorder} pt={8}>
      
      <Heading size="md" display="flex" alignItems="center" gap={3} color={themeFx.accentColor} mb={2}>
        👁️ Laboratório de Visão Computacional 
        <Badge bg={themeFx.badgeBg} color="white" px={2} py={0.5} borderRadius="md">
          HÍBRIDO
        </Badge>
      </Heading>

      <Text color={themeFx.mutedText} fontSize="md" mb={6}>
        Otimize o classificador final (Top-Layer) que processa as características extraídas pela CNN.
      </Text>

      <Flex gap={6} flexWrap="wrap">
        <GlaucomaControls state={state} setters={setters} actions={actions} />
        <GlaucomaEvolutionChart history={state.evolutionHistory} modelType={state.modelType} />
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