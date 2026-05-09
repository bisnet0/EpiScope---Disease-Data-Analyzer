import React, { useState } from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  Button,
  Text,
  Checkbox,
  VStack,
  Icon,
  Flex,
} from "@chakra-ui/react";
import { FaExclamationTriangle } from "react-icons/fa";
import { useWomensHealthThemeFx } from "../styles/theme-fx";

interface WarningAdviceProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (dontShowAgain: boolean) => void;
}

export const WarningAdvice: React.FC<WarningAdviceProps> = ({
  isOpen,
  onClose,
  onConfirm,
}) => {
  const themeFx = useWomensHealthThemeFx();
  const [dontShowAgain, setDontShowAgain] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleAccept = async () => {
    setIsLoading(true);
    await onConfirm(dontShowAgain);
    setIsLoading(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      isCentered
      closeOnOverlayClick={false} // Obriga a clicar no botão
      size="md"
    >
      <ModalOverlay backdropFilter="blur(8px)" bg="blackAlpha.800" />
      <ModalContent
        bg={themeFx.innerBg}
        border="1px solid"
        borderColor={themeFx.cardBorder}
        borderRadius="2xl"
        boxShadow="dark-lg"
      >
        <ModalHeader
          borderBottom="1px solid"
          borderColor="whiteAlpha.100"
          pb={4}
        >
          <Flex align="center" gap={3}>
            <Flex
              p={2}
              bg="red.900"
              color="red.400"
              borderRadius="lg"
              align="center"
              justify="center"
            >
              <Icon as={FaExclamationTriangle} boxSize={5} />
            </Flex>
            <Text color={themeFx.textColor} fontSize="lg">
              Aviso de Conteúdo Sensível
            </Text>
          </Flex>
        </ModalHeader>

        <ModalBody py={6}>
          <VStack spacing={4} align="stretch">
            <Text color={themeFx.mutedText} fontSize="sm" lineHeight="tall">
              Este módulo exibe{" "}
              <strong>imagens reais de procedimentos cirúrgicos</strong>{" "}
              (Laparoscopia), incluindo tecidos internos, instrumentos invasivos
              e possíveis áreas de hemostasia.
            </Text>
            <Text color={themeFx.mutedText} fontSize="sm">
              Ao prosseguir, você confirma que está em um ambiente apropriado
              para auditoria médica e autoriza a exibição deste conteúdo visual.
            </Text>
          </VStack>
        </ModalBody>

        <ModalFooter
          borderTop="1px solid"
          borderColor="whiteAlpha.100"
          pt={4}
          display="flex"
          flexDirection="column"
          alignItems="stretch"
          gap={4}
        >
          <Checkbox
            colorScheme="blue"
            isChecked={dontShowAgain}
            onChange={(e) => setDontShowAgain(e.target.checked)}
            color={themeFx.textColor}
            size="sm"
          >
            Não mostrar este aviso novamente
          </Checkbox>

          <Flex gap={3} w="full">
            <Button
              variant="outline"
              colorScheme="gray"
              flex={1}
              onClick={() => window.history.back()} // Volta a rota se não aceitar
              color={themeFx.mutedText}
              _hover={{ bg: "whiteAlpha.100" }}
              isDisabled={isLoading}
            >
              Sair
            </Button>
            <Button
              colorScheme="blue"
              flex={2}
              onClick={handleAccept}
              isLoading={isLoading}
              loadingText="Salvando..."
            >
              Estou ciente, Continuar
            </Button>
          </Flex>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
