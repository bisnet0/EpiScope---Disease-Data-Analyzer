import React from 'react';
import { Box, Flex, Alert, AlertIcon, Heading, Button, VStack } from '@chakra-ui/react';
import { useDiagnosis } from './hooks/useDiagnosis';
import { formatResponseHtml } from './utils/formatters';
import { DiagnosisInputForm } from './components/DiagnosisInputForm';
import { ProbabilityChart } from './components/ProbabilityChart';
import { AlgorithmsChart } from './components/AlgorithmsChart';
import { useDiagnosisThemeFx } from './styles/theme-fx';
import { ExperimentsPanel } from '../ExperimentsPanel/ExperimentsPanel';

export const DiagnosisArbovirusForm: React.FC = () => {
  const { form, state, actions, charts } = useDiagnosis();
  const themeFx = useDiagnosisThemeFx();

  return (
    <Box w="full" maxW="1800px" mx="auto" pb={10}>
      <VStack spacing={8} align="stretch">
        
        {/* Formulário Principal */}
        <DiagnosisInputForm
          textDescription={form.textDescription}
          setTextDescription={form.setTextDescription}
          age={form.age}
          setAge={form.setAge}
          sex={form.sex}
          setSex={form.setSex}
          loading={state.loading}
          onSubmit={actions.submitDiagnosis}
        />

        {/* Área de Resultados */}
        <Box>
          {state.error && (
            <Alert status="error" borderRadius="md" mb={6}>
              <AlertIcon />
              {state.error}
            </Alert>
          )}

          {state.result && (
            <Box 
              bg={themeFx.cardBg} 
              p={{ base: 5, md: 8 }} 
              borderRadius="xl" 
              border="1px solid" 
              borderColor={themeFx.cardBorder} 
              backdropFilter="blur(16px)" 
              boxShadow="lg"
            >
              <Heading size="md" mb={4} color={themeFx.textColor}>
                🤖 Resultado da Análise
              </Heading>
              
              <Box 
                color={themeFx.textColor}
                mb={8} 
                dangerouslySetInnerHTML={{ __html: formatResponseHtml(state.result.friendly_response) }} 
                sx={{
                  'strong': { color: 'blue.500' },
                  'br': { mb: 2 }
                }}
              />

              <Flex wrap="wrap" gap={6}>
                <ProbabilityChart data={charts.diseaseChartData} />
                <AlgorithmsChart
                  data={charts.modelsChartData}
                  winnerModel={state.result.analysis_details.winner_model}
                />
              </Flex>
            </Box>
          )}
        </Box>

        {/* Botão Laboratório de IA */}
        <Flex justify="center" mt={4}>
          <Button
            variant="outline"
            colorScheme="green"
            onClick={() => state.setShowLab(!state.showLab)}
            size="md"
            borderWidth="2px"
          >
            {state.showLab ? 'Fechar Laboratório' : '🔬 Abrir Laboratório de IA (Modo Avançado)'}
          </Button>
        </Flex>

        {/* Painel Avançado */}
        {state.showLab && (
          <Box w="full" animation="fade-in 0.5s">
            <ExperimentsPanel />
          </Box>
        )}

      </VStack>
    </Box>
  );
};