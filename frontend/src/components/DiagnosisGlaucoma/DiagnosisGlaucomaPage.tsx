import React from "react";
import { Box, Flex, Alert, AlertIcon, VStack, Button } from '@chakra-ui/react';
import { useGlaucoma } from "./hooks/useGlaucoma";
import { GlaucomaInputForm } from "./components/GlaucomaInputForm";
import { GlaucomaResultChart } from "./components/GlaucomaResultChart";
import { GlaucomaExperimentsPanel } from "../GlaucomaExperimentsPanel/GlaucomaExperimentsPanel";

export const DiagnosisGlaucomaForm: React.FC = () => {
  const { state, actions, charts } = useGlaucoma();

  return (
    <Box w="full" maxW="1800px" mx="auto" pb={10}>
      <VStack spacing={8} align="stretch">
        
        {/* Formulário */}
        <GlaucomaInputForm
          previewUrl={state.previewUrl}
          loading={state.loading}
          onImageChange={actions.handleImageChange}
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
            <Box animation="fade-in 0.5s">
              <GlaucomaResultChart 
                result={state.result} 
                chartData={charts.chartData} 
              />
            </Box>
          )}
        </Box>

        {/* Botão para o Lab de Visão Computacional */}
        <Flex justify="center" mt={4}>
          <Button
            variant="outline"
            colorScheme="pink"
            onClick={() => state.setShowLab(!state.showLab)}
            size="md"
            borderWidth="2px"
          >
            {state.showLab ? 'Fechar Lab' : '👁️ Abrir Lab de Visão Computacional (AG)'}
          </Button>
        </Flex>

        {/* Painel Avançado Híbrido */}
        {state.showLab && (
          <Box w="full" animation="fade-in 0.5s">
            <GlaucomaExperimentsPanel />
          </Box>
        )}
        
      </VStack>
    </Box>
  );
};