import React from "react";
import {
  Box,
  Flex,
  Text,
  Heading,
  VStack,
  HStack,
  Divider,
  Progress,
  Circle,
  keyframes,
  Badge,
  SimpleGrid,
  Icon,
} from "@chakra-ui/react";
import {
  FaQuoteLeft,
  FaExclamationTriangle,
  FaLightbulb,
  FaVolumeUp,
  FaClock,
  FaHeartbeat,
} from "react-icons/fa";
import { useWomensHealthThemeFx } from "../styles/theme-fx";
import { type AnalysisData } from "../types";

interface EmotionalSpectrumProps {
  data: AnalysisData | null;
}

const EMOTION_COLORS: Record<string, string> = {
  angry: "red",
  disgust: "green",
  fear: "purple",
  happy: "yellow",
  sad: "blue",
  surprise: "cyan",
  neutral: "gray",
};

const pulseRing = keyframes`
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.5; }
`;

export const EmotionalSpectrum: React.FC<EmotionalSpectrumProps> = ({
  data,
}) => {
  const theme = useWomensHealthThemeFx();
  if (!data) return null;

  const pulseAnimation = `${pulseRing} 2s infinite ease-in-out`;
  const isAudio = data.source_type === "audio";

  return (
    <Box
      p={6}
      bg={theme.cardBg}
      borderRadius="2xl"
      border="1px solid"
      borderColor={theme.cardBorder}
      backdropFilter="blur(12px)"
      boxShadow="2xl"
    >
      {/* HEADER: Perfil Clínico */}
      <VStack align="start" spacing={1}>
        <Text
          fontSize="xs"
          textTransform="uppercase"
          letterSpacing="widest"
          color={theme.mutedText}
          fontWeight="bold"
        >
          Perfil Biopsicossocial
        </Text>
        <Heading size="md" color={theme.textColor} letterSpacing="tight">
          {data.emotional_blend.replace(/_/g, " ")}
        </Heading>
        <HStack spacing={2} mt={2}>
          <Circle
            size="8px"
            bg={isAudio ? "purple.400" : "green.400"}
            animation={pulseAnimation}
          />
          <Text fontSize="xs" color={theme.mutedText}>
            {isAudio ? "Análise Vocal Concluída" : "Análise Facial Concluída"}
          </Text>
        </HStack>
      </VStack>

      <Divider my={5} borderColor={theme.cardBorder} />

      {/* BODY VÍDEO: DeepFace */}
      {!isAudio && data.emotion_distribution && (
        <VStack spacing={4} align="stretch">
          {Object.entries(data.emotion_distribution)
            .sort(([, a], [, b]) => b - a)
            .map(([emotion, value]) => {
              const isDominant = emotion === data.dominant_emotion;
              return (
                <Box key={emotion}>
                  <Flex justify="space-between" align="flex-end" mb={1.5}>
                    <Text
                      fontSize="xs"
                      fontWeight="bold"
                      textTransform="uppercase"
                      color={isDominant ? theme.textColor : theme.mutedText}
                    >
                      {emotion}{" "}
                      {isDominant && (
                        <Text as="span" fontSize="2xs" color="blue.400" ml={2}>
                          (Dominante)
                        </Text>
                      )}
                    </Text>
                    <Text
                      fontSize="xs"
                      fontFamily="mono"
                      color={theme.mutedText}
                    >
                      {(value * 100).toFixed(1)}%
                    </Text>
                  </Flex>
                  <Progress
                    value={value * 100}
                    size="sm"
                    colorScheme={EMOTION_COLORS[emotion] || "gray"}
                    borderRadius="full"
                    bg="whiteAlpha.100"
                    hasStripe={isDominant}
                    isAnimated={isDominant}
                  />
                </Box>
              );
            })}
        </VStack>
      )}

      {/* BODY ÁUDIO: Librosa & Insights */}
      {isAudio && (
        <VStack spacing={5} align="stretch">
          {/* Transcrição */}
          {data.transcription_snippet && (
            <Box
              p={4}
              bg="whiteAlpha.50"
              borderRadius="lg"
              borderLeft="4px solid"
              borderColor="purple.400"
            >
              <Icon as={FaQuoteLeft} color="purple.400" mb={2} />
              <Text fontSize="sm" fontStyle="italic" color={theme.textColor}>
                "{data.transcription_snippet.trim()}"
              </Text>
            </Box>
          )}

          {/* Alertas */}
          {data.alerts && data.alerts.length > 0 && (
            <Box>
              {data.alerts.map((alert, idx) => (
                <Flex
                  key={idx}
                  align="start"
                  p={3}
                  bg="red.900"
                  borderRadius="md"
                  mb={2}
                >
                  <Icon
                    as={FaExclamationTriangle}
                    color="red.200"
                    mt={1}
                    mr={3}
                  />
                  <Text fontSize="sm" color="red.100" fontWeight="medium">
                    {alert.replace("🚨", "").trim()}
                  </Text>
                </Flex>
              ))}
            </Box>
          )}

          {/* Insights Clínicos */}
          {data.clinical_insights && data.clinical_insights.length > 0 && (
            <Box>
              <Text
                fontSize="xs"
                fontWeight="bold"
                color={theme.mutedText}
                mb={2}
                textTransform="uppercase"
              >
                Insights Clínicos
              </Text>
              {data.clinical_insights.map((insight, idx) => (
                <Flex key={idx} align="center" mb={2}>
                  <Icon as={FaLightbulb} color="yellow.400" mr={2} />
                  <Text fontSize="sm" color={theme.textColor}>
                    {insight}
                  </Text>
                </Flex>
              ))}
            </Box>
          )}

          {/* Features Raw (Grid de Estatísticas) */}
          {data.raw_features && (
            <SimpleGrid columns={2} spacing={3} pt={2}>
              <Box
                p={3}
                bg="blackAlpha.300"
                borderRadius="md"
                border="1px solid"
                borderColor={theme.cardBorder}
              >
                <Flex align="center" mb={1}>
                  <Icon as={FaVolumeUp} color="cyan.400" mr={2} />
                  <Text fontSize="xs" color={theme.mutedText}>
                    HESITAÇÃO
                  </Text>
                </Flex>
                <Text fontSize="lg" fontWeight="bold" color={theme.textColor}>
                  {(data.raw_features.hesitation_ratio * 100).toFixed(1)}%
                </Text>
              </Box>
              <Box
                p={3}
                bg="blackAlpha.300"
                borderRadius="md"
                border="1px solid"
                borderColor={theme.cardBorder}
              >
                <Flex align="center" mb={1}>
                  <Icon as={FaClock} color="cyan.400" mr={2} />
                  <Text fontSize="xs" color={theme.mutedText}>
                    DURAÇÃO
                  </Text>
                </Flex>
                <Text fontSize="lg" fontWeight="bold" color={theme.textColor}>
                  {data.raw_features.total_duration_sec}s
                </Text>
              </Box>
            </SimpleGrid>
          )}
        </VStack>
      )}

      {/* FOOTER: Metadados Dinâmicos */}
      <Flex
        pt={4}
        mt={5}
        borderTop="1px solid"
        borderColor={theme.cardBorder}
        justify="space-between"
        align="center"
        fontSize="xs"
        color={theme.mutedText}
        fontWeight="medium"
        textTransform="uppercase"
      >
        {isAudio ? (
          <>
            <Text>Engine: Librosa Audio</Text>
            <Text>Contexto: {data.emotional_blend}</Text>
          </>
        ) : (
          <>
            <Text>Frames: {data.total_frames_analyzed}</Text>
            <Text>Engine: DeepFace v0.0.92</Text>
          </>
        )}
      </Flex>
    </Box>
  );
};
