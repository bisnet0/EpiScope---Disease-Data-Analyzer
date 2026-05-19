import React, { Activity, useState } from "react";
import { Box, Flex, Heading, Text, Grid, Icon } from "@chakra-ui/react";
import { VideoAnalyzer } from "./components/VideoAnalyzer";
import { AudioAnalyzer } from "./components/AudioAnalyzer";
import { EmotionalSpectrum } from "./components/EmotionalSpectrum";

import { useVideoAnalyzer } from "./hooks/useVideoAnalyzer";
import { useAudioAnalyzer } from "./hooks/useAudioAnalyzer";
import { useEmotionalSpectrum } from "./hooks/useEmotionalSpectrum";

import { useWomensHealthThemeFx } from "./styles/theme-fx";
import { EmojiAstonished, EmojiExpressionless, EmojiGrimace, Heart } from "react-bootstrap-icons";
import { GiHappySkull } from "react-icons/gi";
import { PiMaskHappy } from "react-icons/pi";

export const WomensHealthModule: React.FC = () => {
  // 1. Invoca os micro-hooks
  const { videoStatus, videoError, processVideo, resetVideoState } =
    useVideoAnalyzer();
  const { audioStatus, audioError, processAudio, resetAudioState } =
    useAudioAnalyzer();
  const {
    spectrumData,
    formatAndSetVideoResult,
    formatAndSetAudioResult,
    clearSpectrum,
  } = useEmotionalSpectrum();

  // 2. Estado local
  const [consultationType, setConsultationType] = useState("TRIAGEM_VIOLENCIA");
  const themeFx = useWomensHealthThemeFx();
  // Funções de Handler para conectar a API ao Gráfico
  const handleProcessVideo = async (file: File, type: string) => {
    try {
      const rawData = await processVideo(file, type);
      formatAndSetVideoResult(rawData);
    } catch (e) {
      // O erro já é tratado e exibido no componente filho pelo hook
    }
  };

  const handleProcessAudio = async (file: File, type: string) => {
    try {
      const rawData = await processAudio(file, type);
      formatAndSetAudioResult(rawData);
    } catch (e) {
      // Erro tratado pelo hook
    }
  };

  const handleContextChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setConsultationType(e.target.value);
    clearSpectrum();
    resetVideoState();
    resetAudioState();
  };

  return (
    <Box
      p={6}
      bg={themeFx.cardBg}
      border="1px solid"
      borderColor={themeFx.cardBorder}
      borderRadius="2xl"
      backdropFilter="blur(12px)"
      boxShadow="2xl"
    >
      <Flex direction="column" h="full" gap={6} color="white">
        {/* HEADER */}
        <Flex
          direction={{ base: "column", sm: "row" }}
          justify="space-between"
          align={{ base: "flex-start", sm: "flex-end" }}
          borderBottom="1px solid"
          borderColor="whiteAlpha.200"
          pb={4}
        >
          <Box>
           <Heading
        size="md"
        mb={2}
        color={themeFx.textColor}
        display="flex"
        alignItems="center"
        gap={3}
      >
        <Icon as={PiMaskHappy} color={themeFx.accentColor} />
       Biomarcadores
       
      </Heading>
            <Text fontSize="sm" color={themeFx.mutedText}>
              Triagem Multimodal com Análise de Microexpressões e Biomarcadores
              Vocais
            </Text>
          </Box>

          <Box mt={{ base: 4, sm: 0 }} w={{ base: "full", sm: "auto" }}>
            <Text
              fontSize="xs"
              fontWeight="semibold"
              color={themeFx.mutedText}
              textTransform="uppercase"
              mb={1}
            >
              Contexto Clínico
            </Text>
            <select
              value={consultationType}
              onChange={handleContextChange}
              className="bg-slate-800 border border-slate-600 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2 outline-none"
              style={{
                backgroundColor: "#1a202c",
                color: "white",
                borderColor: "rgba(255,255,255,0.16)",
              }}
            >
              <option value="TRIAGEM_VIOLENCIA">
                Triagem de Violência/Risco
              </option>
              <option value="POS_PARTO">Acompanhamento Pós-Parto</option>
              <option value="ROTINA_GINECOLOGICA">Rotina Ginecológica</option>
            </select>
          </Box>
        </Flex>

        {/* GRID PRINCIPAL */}
        <Grid templateColumns={{ base: "1fr", xl: "1fr 1fr" }} gap={6}>
          {/* Coluna Esquerda: Inputs */}
          <Flex direction="column" gap={6}>
            <VideoAnalyzer
              consultationType={consultationType}
              status={videoStatus}
              error={videoError}
              onProcessVideo={handleProcessVideo}
            />

            <AudioAnalyzer
              consultationType={consultationType}
              status={audioStatus}
              error={audioError}
              onProcessAudio={handleProcessAudio}
            />
          </Flex>

          {/* Coluna Direita: Output */}
          <Box h="full">
            {spectrumData ? (
              <EmotionalSpectrum data={spectrumData} />
            ) : (
              <Flex
                direction="column"
                align="center"
                justify="center"
                h="full"
                minH="300px"
                border="1px solid"
                borderColor="whiteAlpha.200"
                bg="blackAlpha.300"
                borderRadius="xl"
                p={6}
                textAlign="center"
              >
                <Box
                  as="svg"
                  w={12}
                  h={12}
                  color="gray.600"
                  mb={4}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </Box>
                <Heading size="md" color="gray.400">
                  Aguardando Biomarcadores
                </Heading>
                <Text fontSize="sm" color="gray.500" mt={2} maxW="sm">
                  Faça o upload do vídeo ou áudio da paciente para gerar o
                  espectro emocional e visualizar o perfil clínico
                  biopsicossocial.
                </Text>
              </Flex>
            )}
          </Box>
        </Grid>
      </Flex>
    </Box>
  );
};
