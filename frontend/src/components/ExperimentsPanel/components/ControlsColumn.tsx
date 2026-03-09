import React from 'react';
import { 
  Box, Button, Flex, FormControl, FormLabel, Select, 
  Slider, SliderTrack, SliderFilledTrack, SliderThumb, Text, VStack 
} from '@chakra-ui/react';
import { useExperimentsThemeFx } from '../styles/theme-fx';
import { type ControlsColumnProps } from '../types';

export const ControlsColumn: React.FC<ControlsColumnProps> = ({ state, setters, actions }) => {
  const themeFx = useExperimentsThemeFx();

  return (
    <Box 
      flex="1 1 300px" 
      bg={themeFx.cardBg} 
      p={6} 
      borderRadius="xl" 
      border="1px solid" 
      borderColor={themeFx.cardBorder}
      backdropFilter="blur(16px)"
      boxShadow="lg"
    >
      {/* Botões de IA */}
      <Flex gap={3} mb={6}>
        <Button
          flex={1}
          onClick={actions.handleSuggestParams}
          isDisabled={state.loading}
          bgGradient="linear(to-br, blue.400, teal.400)"
          color="white"
          _hover={{ bgGradient: "linear(to-br, blue.500, teal.500)" }}
        >
          🔮 Oráculo
        </Button>
        <Button
          flex={1}
          onClick={actions.handleRunEvolution}
          isDisabled={state.loading}
          bgGradient="linear(to-br, purple.500, pink.500)"
          color="white"
          _hover={{ bgGradient: "linear(to-br, purple.600, pink.600)" }}
        >
          🧬 Evoluir
        </Button>
      </Flex>

      <Box mt={4} borderTop="1px solid" borderColor={themeFx.cardBorder} pt={4}>
        <Button
          variant="ghost"
          color={themeFx.accentColor}
          size="sm"
          w="full"
          onClick={() => setters.setShowAdvancedGA(!state.showAdvancedGA)}
        >
          {state.showAdvancedGA ? '▼ Ocultar Config Genética' : '▶ Configurar Algoritmo Genético'}
        </Button>

        {state.showAdvancedGA && (
          <VStack spacing={4} mt={4} bg={themeFx.innerBg} p={4} borderRadius="md" border="1px solid" borderColor={themeFx.cardBorder}>
            <FormControl>
              <FormLabel fontSize="sm" color={themeFx.textColor}>Gerações: {state.generations}</FormLabel>
              <Slider min={3} max={20} value={state.generations} onChange={v => setters.setGenerations(v)}>
                <SliderTrack><SliderFilledTrack bg="purple.500" /></SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm" color={themeFx.textColor}>População: {state.popSize}</FormLabel>
              <Slider min={5} max={50} value={state.popSize} onChange={v => setters.setPopSize(v)}>
                <SliderTrack><SliderFilledTrack bg="purple.500" /></SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm" color={themeFx.textColor}>Taxa de Mutação: {Math.round(state.mutationRate * 100)}%</FormLabel>
              <Slider min={0.01} max={0.5} step={0.01} value={state.mutationRate} onChange={v => setters.setMutationRate(v)}>
                <SliderTrack><SliderFilledTrack bg="purple.500" /></SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>
            <Text fontSize="xs" color={themeFx.mutedText} textAlign="center">
              Atenção: Aumentar População/Gerações aumenta o tempo de processamento.
            </Text>
          </VStack>
        )}
      </Box>

      {/* Form Manual */}
      <VStack spacing={5} mt={6} align="stretch">
        <FormControl>
          <FormLabel color={themeFx.textColor}>Algoritmo:</FormLabel>
          <Select 
            value={state.modelType} 
            onChange={e => setters.setModelType(e.target.value)}
            bg={themeFx.inputBg}
            focusBorderColor="green.400"
          >
            <option value="xgboost">XGBoost</option>
            <option value="random_forest">Random Forest</option>
            <option value="decision_tree">Decision Tree</option>
          </Select>
        </FormControl>

        <FormControl>
          <FormLabel color={themeFx.textColor}>Profundidade Máxima (Max Depth): {state.maxDepth}</FormLabel>
          <Slider min={1} max={50} value={state.maxDepth} onChange={v => setters.setMaxDepth(v)}>
            <SliderTrack><SliderFilledTrack bg="green.400" /></SliderTrack>
            <SliderThumb />
          </Slider>
        </FormControl>

        {state.modelType !== 'decision_tree' && (
          <FormControl>
            <FormLabel color={themeFx.textColor}>Nº Estimadores: {state.nEstimators}</FormLabel>
            <Slider min={10} max={1000} step={10} value={state.nEstimators} onChange={v => setters.setNEstimators(v)}>
              <SliderTrack><SliderFilledTrack bg="green.400" /></SliderTrack>
              <SliderThumb />
            </Slider>
          </FormControl>
        )}

        {state.modelType === 'xgboost' && (
          <FormControl>
            <FormLabel color={themeFx.textColor}>Taxa de Aprendizado (LR): {state.learningRate}</FormLabel>
            <Slider min={0.001} max={1.0} step={0.001} value={state.learningRate} onChange={v => setters.setLearningRate(v)}>
              <SliderTrack><SliderFilledTrack bg="green.400" /></SliderTrack>
              <SliderThumb />
            </Slider>
          </FormControl>
        )}

        <Button
          onClick={actions.handleRunExperiment}
          isLoading={state.loading}
          loadingText={state.loadingMessage || 'Processando...'}
          colorScheme="green"
          size="lg"
          w="full"
          mt={2}
        >
          🧪 Rodar Teste Único
        </Button>
      </VStack>
    </Box>
  );
};