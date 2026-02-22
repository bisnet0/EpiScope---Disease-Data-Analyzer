import React from 'react';
import { 
  Box, Flex, Text, Icon, VStack, Drawer, DrawerBody, 
  DrawerHeader, DrawerOverlay, DrawerContent, DrawerCloseButton 
} from '@chakra-ui/react';
import { NAV_ITEMS, type AppMode } from './nav-config';
import { useAppThemeFx } from '../../styles/app-theme-fx';

interface Props {
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<Props> = ({ mode, setMode, isOpen, onClose }) => {
  const themeFx = useAppThemeFx();

  // O conteúdo dos botões, isolado para reutilizarmos no Desktop e Mobile
  const SidebarContent = () => (
    <VStack spacing={2} align="stretch" w="100%">
      <Text fontSize="xs" fontWeight="bold" color={themeFx.mutedText} textTransform="uppercase" mb={2} px={4}>
        Módulos
      </Text>
      {NAV_ITEMS.map((item) => {
        const isActive = mode === item.id;
        return (
          <Flex
            key={item.id}
            align="center"
            px={4}
            py={3}
            mx={2}
            borderRadius="lg"
            cursor="pointer"
            bg={isActive ? themeFx.navActiveBg : 'transparent'}
            color={isActive ? themeFx.navActiveColor : themeFx.mutedText}
            fontWeight={isActive ? "bold" : "medium"}
            transition="all 0.2s"
            _hover={{ bg: isActive ? themeFx.navActiveBg : themeFx.navHoverBg }}
            onClick={() => {
              setMode(item.id);
              onClose(); // Fecha o drawer no mobile ao clicar
            }}
          >
            <Icon as={item.icon} boxSize={5} mr={4} />
            <Text fontSize="sm">{item.label}</Text>
          </Flex>
        );
      })}
    </VStack>
  );

  return (
    <>
      {/* SIDEBAR DESKTOP (Fixa na esquerda, abaixo do Header de 70px) */}
      <Box
        display={{ base: 'none', md: 'block' }}
        position="fixed"
        left={0}
        top="70px" 
        w="250px"
        h="calc(100vh - 70px)"
        bg={themeFx.sidebarBg}
        borderRight="1px solid"
        borderColor={themeFx.headerBorder}
        py={6}
        zIndex={900}
      >
        <SidebarContent />
      </Box>

      {/* DRAWER MOBILE (Aparece ao clicar no Hamburger) */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay display={{ base: 'block', md: 'none' }} />
        <DrawerContent bg={themeFx.sidebarBg} display={{ base: 'block', md: 'none' }}>
          <DrawerCloseButton color={themeFx.textColor} />
          <DrawerHeader borderBottomWidth="1px" borderColor={themeFx.headerBorder} color={themeFx.textColor}>
            Menu de Navegação
          </DrawerHeader>
          <DrawerBody pt={6} px={0}>
            <SidebarContent />
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
};