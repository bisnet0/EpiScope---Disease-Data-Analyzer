// src/components/DiagnosisXRay/styles/theme-fx.ts

import { useColorModeValue } from '@chakra-ui/react';

export const useXRayThemeFx = () => {
  return {
    cardBg: useColorModeValue('rgba(255, 255, 255, 0.85)', 'rgba(30, 34, 45, 0.85)'),
    cardSoftBg: useColorModeValue('rgba(255, 255, 255, 0.2)', 'rgba(33, 37, 47, 0.73)'),
    cardBorder: useColorModeValue('gray.200', 'gray.700'),
    textColor: useColorModeValue('gray.800', 'white'),
    mutedText: useColorModeValue('gray.600', 'gray.400'),
    accentColor: 'cyan.400',
    accentHover: 'cyan.500',
    barNormal: 'green',
    barPneumonia: 'red',
    barTuberculosis: 'orange',
  };
};