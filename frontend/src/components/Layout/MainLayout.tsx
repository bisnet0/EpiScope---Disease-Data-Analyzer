import React, { useState } from "react";
import {
  Box,
  Flex,
  Center,
  Spinner,
  Text,
  Image,
  useDisclosure,
  VStack,
  Heading,
} from "@chakra-ui/react";
import { useAuth } from "../../context/AuthContext";
import { type AppMode } from "./nav-config";
import { useAppThemeFx } from "../../styles/app-theme-fx";

// Views
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { Footer } from "./Footer";
import { DashboardPage } from "../Dashboard/DashboardPage";
import { DiagnosisArbovirusForm } from "../DiagnosisArbovirus/DiagnosisArbovirusPage";
import { DiagnosisGlaucomaForm } from "../DiagnosisGlaucoma/DiagnosisGlaucomaPage";
import { DiagnosisDAppForm } from "../DiagnosisDApp/DiagnosisDAppForm";
import { DiagnosisXRayForm } from "../DiagnosisXRay/components/DiagnosisXRay";
import { LoginForm } from "../Login/LoginForm";
import AgentChat from "../AgentChat/AgentChat";

export const MainLayout: React.FC = () => {
  const [mode, setMode] = useState<AppMode>("dashboard");
  const { isOpen, onOpen, onClose } = useDisclosure();
  const themeFx = useAppThemeFx();
  const { isAuthenticated, loadingAuth } = useAuth();

  if (loadingAuth) {
    return (
      <Center h="100vh" bg={themeFx.appBg} flexDirection="column" gap={4}>
        <Spinner size="xl" color="blue.500" thickness="4px" />
        <Text color={themeFx.textColor} fontWeight="bold">
          Carregando Sessão...
        </Text>
      </Center>
    );
  }

  // --- ÁREA DE LOGIN REFATORADA (SPLIT SCREEN) ---
  if (!isAuthenticated) {
    return (
      <Flex h="100vh" bg={themeFx.appBg} overflow="hidden">
        {/* LADO ESQUERDO: Logo + Apresentação + Formulário */}
        <Flex
          flex={1}
          direction="column"
          justify="center"
          align="center"
          p={{ base: 4, md: 8 }}
          overflowY="auto"
        >
          <VStack spacing={10} w="full" maxW="md">
            {/* 🚀 CABEÇALHO LADO A LADO (Igual ao Photoshop) */}
            <Flex align="center" justify="center" gap={4} w="full">
              <Image
                src="/EpiScope.png"
                alt="EpiScope Logo"
                w={{ base: "80px", md: "110px" }} // Tamanho ajustado para parear com o texto
                dropShadow="lg"
              />

              <Flex direction="column" align="flex-start" justify="center">
                <Text
                  fontFamily="'Poppins', sans-serif"
                  fontWeight="400" // Regular
                  fontSize={{ base: "sm", md: "lg" }}
                  color={themeFx.textColor}
                  mb="-1" // Puxa o "EpiScope" levemente pra cima pra ficar mais grudado
                >
                  Seja muito bem-vindo ao
                </Text>

                <Heading
                  as="h1"
                  fontFamily="'Poppins', sans-serif"
                  fontWeight="100" // Thin
                  fontSize={{ base: "4xl", md: "5xl" }}
                  color={themeFx.textColor}
                  letterSpacing="tight"
                  lineHeight="1"
                  display="flex"
                  alignItems="baseline"
                  gap={2}
                >
                  EpiScope{" "}
                  <Text
                    as="span"
                    fontWeight="100"
                    fontSize={{ base: "3xl", md: "5xl" }}
                  >
                    AI
                  </Text>
                </Heading>
              </Flex>
            </Flex>

            {/* O Card do Login */}
            <LoginForm />
          </VStack>
        </Flex>

        {/* LADO DIREITO: Imagem Hero */}
        <Box
          display={{ base: "none", lg: "block" }}
          flex={1}
          bg="gray.900"
          position="relative"
        >
          <Image
            // ⚠️ COLOQUE O CAMINHO DA SUA IMAGEM DE DESKTOP AQUI ⚠️
            src="/public/Dr.EpiScope.png"
            alt="Login Hero"
            objectFit="cover" // Garante que a imagem cubra toda a área sem distorcer
            w="full"
            h="full"
          />
        </Box>
      </Flex>
    );
  }

  // --- APLICAÇÃO PRINCIPAL (Autenticado) ---
  return (
    <Flex minH="100vh" bg={themeFx.appBg} transition="background 0.2s">
      <Navbar onOpenSidebar={onOpen} />
      <Sidebar
        mode={mode}
        setMode={setMode}
        isOpen={isOpen}
        onClose={onClose}
      />

      <Flex
        flex={1}
        direction="column"
        ml={{ base: 0, md: "250px" }}
        w={{ base: "100%", md: "calc(100% - 250px)" }}
        pt="70px"
      >
        <Box
          as="main"
          flex={1}
          p={{ base: 4, md: 8 }}
          w="100%"
          overflowX="hidden"
          animation="fade-in 0.4s"
        >
          {mode === "dashboard" && <DashboardPage />}
          {mode === "web2" && <DiagnosisArbovirusForm />}
          {mode === "web3" && <DiagnosisDAppForm />}
          {mode === "image" && <DiagnosisGlaucomaForm />}
          {mode === "x-ray" && <DiagnosisXRayForm />}

        </Box>

        <Footer />
      </Flex>
      <AgentChat />
    </Flex>
  );
};
