import React, { useState, useRef } from 'react';
import { 
  Box, Flex, Text, Button, Heading, Icon, VStack, Center, Spinner 
} from '@chakra-ui/react';
import { 
  FaMicrophone, 
  FaFileAudio, 
  FaCheckCircle, 
  FaExclamationTriangle 
} from 'react-icons/fa';

import { useWomensHealthThemeFx } from '../styles/theme-fx';
import { type AnalysisStatus } from '../types';

interface AudioAnalyzerProps {
  consultationType: string;
  status: AnalysisStatus;
  error: string | null;
  onProcessAudio: (file: File, type: string) => void;
}

export const AudioAnalyzer: React.FC<AudioAnalyzerProps> = ({ 
  consultationType,
  status,
  error,
  onProcessAudio
}) => {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const theme = useWomensHealthThemeFx();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      // Validação para aceitar apenas arquivos de áudio (.wav, .mp3, etc)
      if (selectedFile.type.startsWith('audio/')) {
        setFile(selectedFile);
      }
    }
  };

  const handleStartAnalysis = () => {
    if (file) {
      onProcessAudio(file, consultationType);
    }
  };

  return (
    <Box p={5} bg={theme.innerBg} borderRadius="2xl" border="1px solid" borderColor={theme.cardBorder}>
      {/* HEADER */}
      <Flex align="center" justify="space-between" mb={4}>
        <Heading size="sm" color={theme.textColor} display="flex" alignItems="center">
          <Icon as={FaMicrophone} mr={2} color="purple.400" />
          ANÁLISE VOCAL (ÁUDIO)
        </Heading>
        <Text fontSize="xs" fontWeight="bold" color={theme.mutedText} textTransform="uppercase">
          {consultationType.replace('_', ' ')}
        </Text>
      </Flex>

      <VStack spacing={4} align="stretch">
        
        {/* DROPZONE */}
        <Center
          p={6}
          flexDirection="column"
          border="2px dashed"
          borderColor={file ? "purple.400" : theme.cardBorder}
          borderRadius="xl"
          bg={file ? "whiteAlpha.100" : "transparent"}
          cursor="pointer"
          transition="all 0.2s"
          _hover={{ borderColor: 'purple.400', bg: 'whiteAlpha.50' }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            type="file" 
            accept="audio/*" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
          />
          
          {file ? (
            <VStack spacing={1}>
              <Icon as={FaCheckCircle} fontSize="3xl" color="green.400" mb={2} />
              <Text fontWeight="bold" color={theme.textColor} textAlign="center" noOfLines={1}>
                {file.name}
              </Text>
              <Text fontSize="sm" color={theme.mutedText}>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </Text>
            </VStack>
          ) : (
            <VStack spacing={2}>
              <Icon as={FaFileAudio} fontSize="3xl" color={theme.mutedText} />
              <Text color={theme.mutedText} textAlign="center" fontSize="sm">
                Selecione o áudio da consulta
              </Text>
            </VStack>
          )}
        </Center>

        {/* MENSAGEM DE ERRO ESPECÍFICA DO ÁUDIO */}
        {status === 'error' && error && (
          <Flex align="center" p={3} bg="red.900" color="red.100" borderRadius="md" fontSize="sm">
            <Icon as={FaExclamationTriangle} mr={2} />
            <Text>{error}</Text>
          </Flex>
        )}

        {/* BOTÃO DE AÇÃO / SPINNER */}
        {status === 'analyzing' ? (
          <Flex align="center" justify="center" p={2} color="purple.400">
            <Spinner size="sm" mr={3} />
            <Text fontSize="sm" fontWeight="bold">Extraindo biomarcadores vocais...</Text>
          </Flex>
        ) : (
          <Button
            colorScheme="purple"
            size="md"
            width="full"
            onClick={handleStartAnalysis}
            isDisabled={!file}
          >
            {status === 'success' ? 'Reanalisar Áudio' : 'Analisar Sentimento Vocal'}
          </Button>
        )}
      </VStack>
    </Box>
  );
};