import React, { useState } from 'react';
import { Box, Flex, Center, Spinner, Text, Image, useDisclosure } from '@chakra-ui/react';
import { useAuth } from '../../context/AuthContext';
import { type AppMode } from './nav-config';
import { useAppThemeFx } from '../../styles/app-theme-fx';

// Views
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { DashboardPage } from '../Dashboard/DashboardPage';
import { DiagnosisArbovirusForm } from '../DiagnosisArbovirus/DiagnosisArbovirusPage';
import { DiagnosisGlaucomaForm } from '../DiagnosisGlaucoma/DiagnosisGlaucomaPage';
import { DiagnosisDAppForm } from '../DiagnosisDApp/DiagnosisDAppForm';
import { LoginForm } from '../Login/LoginForm';
import AgentChat from '../AgentChat/AgentChat';

export const MainLayout: React.FC = () => {
  const [mode, setMode] = useState<AppMode>("dashboard");
  const { isOpen, onOpen, onClose } = useDisclosure(); // Hook nativo do Chakra pra Drawer
  const themeFx = useAppThemeFx();
  const { isAuthenticated, loadingAuth } = useAuth();

  if (loadingAuth) {
    return (
      <Center h="100vh" bg={themeFx.appBg} flexDirection="column" gap={4}>
        <Spinner size="xl" color="blue.500" thickness="4px" />
        <Text color={themeFx.textColor} fontWeight="bold">Carregando Sessão...</Text>
      </Center>
    );
  }

  if (!isAuthenticated) {
    return (
      <Box bg={themeFx.appBg} minH="100vh">
        <Center pt={10} pb={4}>
          <Image src="/EpiScope.png" alt="EpiScope Logo" w="150px" dropShadow="lg" />
        </Center>
        <LoginForm />
      </Box>
    );
  }

  return (
    <Flex minH="100vh" bg={themeFx.appBg} transition="background 0.2s">
      
      {/* 1. Navbar Topo (100% width) */}
      <Navbar onOpenSidebar={onOpen} />

      {/* 2. Menu Lateral (Escondido no mobile, exibe via Drawer) */}
      <Sidebar mode={mode} setMode={setMode} isOpen={isOpen} onClose={onClose} />

      {/* 3. Área de Conteúdo Central */}
      <Flex 
        flex={1} 
        direction="column" 
        ml={{ base: 0, md: "250px" }} // Empurra o conteúdo pra direita em telas grandes devido a sidebar fixa
        pt="70px" // Empurra o conteúdo pra baixo devido à Navbar fixa de 70px
      >
        <Box as="main" flex={1} p={{ base: 4, md: 8 }} animation="fade-in 0.4s">
          {mode === "dashboard" && <DashboardPage />}
          {mode === "web2" && <DiagnosisArbovirusForm />}
          {mode === "web3" && <DiagnosisDAppForm />}
          {mode === "image" && <DiagnosisGlaucomaForm />}
        </Box>

        <Footer />
      </Flex>

      {/* Widget Flutuante sempre visível */}
      <AgentChat />

    </Flex>
  );
};