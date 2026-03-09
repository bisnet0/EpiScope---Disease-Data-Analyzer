import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

const config: ThemeConfig = {
  initialColorMode: 'dark', // Padrão escuro
  useSystemColorMode: false,
}

const theme = extendTheme({
  config,
  // Aqui está o pulo do gato!
  semanticTokens: {
    colors: {
      // Cores genéricas da aplicação (pode usar em qualquer lugar)
      appBg: { default: 'gray.50', _dark: '#242424' },
      appText: { default: 'gray.800', _dark: 'white' },
      
      // Cores específicas do Dr. EpiScope
      'chat.containerBg': { default: 'rgba(255, 255, 255, 0.95)', _dark: 'rgba(36, 36, 36, 0.95)' },
      'chat.headerBg': { default: 'gray.800', _dark: 'gray.900' },
      'chat.areaBg': { default: 'gray.50', _dark: 'gray.800' },
      'chat.agentMsgBg': { default: 'white', _dark: 'gray.700' },
      'chat.agentMsgText': { default: 'gray.800', _dark: 'white' },
      'chat.inputAreaBg': { default: 'rgba(0, 0, 0, 0.16)', _dark: 'gray.900' },
      'chat.inputBg': { default: 'gray.100', _dark: 'gray.800' },
      'chat.borderColor': { default: 'rgba(0, 0, 0, 0.16)', _dark: 'rgba(255, 255, 255, 0.1)' },
      'chat.mutedText': { default: 'gray.500', _dark: 'gray.400' },
    }
  }
})

export default theme