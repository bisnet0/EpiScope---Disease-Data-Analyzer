import React from 'react';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Input, 
  Select, 
  Textarea, 
  VStack,
  keyframes,
  Heading,
  Text,
  Icon
} from '@chakra-ui/react';
import { useDiagnosisThemeFx } from '../styles/theme-fx';
import { type FormProps } from '../types';
import { FaMosquito } from 'react-icons/fa6';

export const DiagnosisInputForm: React.FC<FormProps> = ({
  textDescription, setTextDescription, age, setAge, sex, setSex, loading, onSubmit
}) => {
  const pulse = keyframes`
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  `;
  const themeFx = useDiagnosisThemeFx();

  return (
    <Box 
      as="form" 
      onSubmit={onSubmit} 
      bg={themeFx.cardBg} 
      p={{ base: 5, md: 8 }} 
      borderRadius="xl" 
      border="1px solid" 
      borderColor={themeFx.cardBorder} 
      backdropFilter="blur(16px)" 
      boxShadow="lg"
      w="full"
    >
      <VStack spacing={5} align="stretch">
        
        <Heading
              size="md"
              display="flex"
              alignItems="center"
              color={themeFx.textColor}
            >
              <Icon
                as={FaMosquito}
                color={themeFx.mosquitoBg}
                mr={2}
                boxSize={5}
              />
              Análise Clínica
            </Heading>

        <FormControl isRequired>
          <FormLabel color={themeFx.textColor}>Descreva seus sintomas:</FormLabel>
          <Textarea
            bg={themeFx.inputBg}
            focusBorderColor="blue.400"
            value={textDescription}
            onChange={(e) => setTextDescription(e.target.value)}
            placeholder="Ex: Febre alta, dor atrás dos olhos..."
            rows={4}
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel color={themeFx.textColor}>Idade:</FormLabel>
          <Input
            type="number"
            bg={themeFx.inputBg}
            focusBorderColor="blue.400"
            value={age}
            onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))}
            min={0}
          />
        </FormControl>

        <FormControl>
          <FormLabel color={themeFx.textColor}>Sexo:</FormLabel>
          <Select 
            bg={themeFx.inputBg} 
            focusBorderColor="blue.400" 
            value={sex} 
            onChange={(e) => setSex(e.target.value)}
          >
            <option value="M">Masculino</option>
            <option value="F">Feminino</option>
          </Select>
        </FormControl>

        <Button 
          type="submit" 
          colorScheme="green" 
          size="lg" 
          isLoading={loading} 
          loadingText="Consultando Maestro e Auditoria..."
          mt={2}
        >
          Rodar Diagnóstico
        </Button>
        {loading && (
           <Text fontSize="xs" color="gray.500" textAlign="center" animation={`${pulse} 1.5s infinite`}>
             ⚙️ Processando modelos técnicos e registrando na Blockchain...
           </Text>
        )}
      </VStack>
    </Box>
  );
};