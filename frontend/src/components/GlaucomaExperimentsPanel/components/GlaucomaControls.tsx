import React from 'react';
import { 
  Box, Button, FormControl, FormLabel, Select, 
  Slider, SliderTrack, SliderFilledTrack, SliderThumb, Text, VStack 
} from '@chakra-ui/react';
import { useGlaucomaExpThemeFx } from '../styles/theme-fx';
import { type GlaucomaControlsProps } from '../types';


export const GlaucomaControls: React.FC<GlaucomaControlsProps> = ({ state, setters, actions }) => {
  const themeFx = useGlaucomaExpThemeFx();

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
      <FormControl mb={4}>
        <FormLabel color={themeFx.textColor}>Classificador Final (Head):</FormLabel>
        <Select 
          value={state.modelType} 
          onChange={e => setters.setModelType(e.target.value)}
          bg={themeFx.inputBg}
          focusBorderColor="pink.400"
        >
          <option value="xgboost">XGBoost (Gradient Boosting)</option>
          <option value="random_forest">Random Forest</option>
          <option value="decision_tree">Decision Tree</option>
        </Select>
      </FormControl>

      <Box my={6} borderTop="1px solid" borderColor={themeFx.cardBorder} pt={4}>
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
                <SliderTrack><SliderFilledTrack bg="pink.500" /></SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm" color={themeFx.textColor}>População: {state.popSize}</FormLabel>
              <Slider min={5} max={50} value={state.popSize} onChange={v => setters.setPopSize(v)}>
                <SliderTrack><SliderFilledTrack bg="pink.500" /></SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="sm" color={themeFx.textColor}>Taxa de Mutação: {Math.round(state.mutationRate * 100)}%</FormLabel>
              <Slider min={0.01} max={0.5} step={0.01} value={state.mutationRate} onChange={v => setters.setMutationRate(v)}>
                <SliderTrack><SliderFilledTrack bg="pink.500" /></SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>
          </VStack>
        )}
      </Box>

      {/* Resultados em ReadOnly (Mostra o que a IA escolheu após evoluir) */}
      <VStack spacing={5} align="stretch" opacity={0.7} pointerEvents="none">
        <FormControl>
          <FormLabel color={themeFx.textColor}>Profundidade Resultante: {state.maxDepth}</FormLabel>
          <Slider value={state.maxDepth} min={1} max={50} isReadOnly>
            <SliderTrack><SliderFilledTrack bg="gray.500" /></SliderTrack>
            <SliderThumb />
          </Slider>
        </FormControl>

        {state.modelType !== 'decision_tree' && (
          <FormControl>
            <FormLabel color={themeFx.textColor}>Estimadores Resultantes: {state.nEstimators}</FormLabel>
            <Slider value={state.nEstimators} min={10} max={1000} isReadOnly>
              <SliderTrack><SliderFilledTrack bg="gray.500" /></SliderTrack>
              <SliderThumb />
            </Slider>
          </FormControl>
        )}
      </VStack>

      <Button
        onClick={actions.handleRunEvolution}
        isLoading={state.loading}
        loadingText="🧬 Evoluindo Rede..."
        bgGradient="linear(to-r, pink.500, purple.500)"
        color="white"
        _hover={{ bgGradient: "linear(to-r, pink.600, purple.600)" }}
        size="lg"
        w="full"
        mt={8}
      >
        🧬 Iniciar Algoritmo Genético
      </Button>
    </Box>
  );
};