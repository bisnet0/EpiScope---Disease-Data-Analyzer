// src/components/layout/Sidebar.tsx
import React, { useState } from "react";
import {
  Box,
  Flex,
  Text,
  Icon,
  VStack,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Collapse,
  Image,
} from "@chakra-ui/react";
import { FiChevronDown, FiChevronRight } from "react-icons/fi";
import { NAV_ITEMS, type AppMode } from "./nav-config";
import { useAppThemeFx } from "../../styles/app-theme-fx";

interface Props {
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<Props> = ({
  mode,
  setMode,
  isOpen,
  onClose,
}) => {
  const themeFx = useAppThemeFx();
  // Estado para controlar quais submenus estão abertos (ex: { 'WOMENS_HEALTH_MENU': true })
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({});

  const toggleMenu = (menuId: string) => {
    setOpenMenus((prev) => ({ ...prev, [menuId]: !prev[menuId] }));
  };

  const SidebarContent = () => (
    <VStack spacing={2} align="stretch" w="100%">
      {NAV_ITEMS.map((item) => {
        const hasChildren = item.children && item.children.length > 0;

        // Verifica se algum filho está ativo para manter o menu "pai" realçado (opcional)
        const isChildActive = hasChildren
          ? item.children!.some((child) => mode === child.id)
          : false;

        const isActive = mode === item.id || isChildActive;
        const isOpenMenu = openMenus[item.id] || isChildActive;

        return (
          <Box key={item.id}>
            <Flex
              align="center"
              justify="space-between"
              px={4}
              py={3}
              mx={2}
              borderRadius="lg"
              cursor="pointer"
              bg={
                isActive && !hasChildren ? themeFx.navActiveBg : "transparent"
              }
              color={
                isActive || isChildActive
                  ? themeFx.navActiveColor
                  : themeFx.mutedText
              }
              fontWeight={isActive || isChildActive ? "bold" : "medium"}
              transition="all 0.2s"
              _hover={{ bg: themeFx.navHoverBg }}
              onClick={() => {
                if (hasChildren) {
                  toggleMenu(item.id);
                } else {
                  setMode(item.id);
                  onClose(); // Fecha o drawer no mobile após o clique
                }
              }}
            >
              <Flex align="center">
                <Icon as={item.icon} boxSize={5} mr={4} />
                <Text fontSize="sm">{item.label}</Text>
              </Flex>

              {/* Ícone de Seta para Submenus */}
              {hasChildren && (
                <Icon
                  as={isOpenMenu ? FiChevronDown : FiChevronRight}
                  boxSize={4}
                  transition="all 0.2s"
                />
              )}
            </Flex>

            {/* Renderização do Dropdown / Submenu */}
            {hasChildren && (
              <Collapse in={isOpenMenu} animateOpacity>
                <VStack spacing={1} align="stretch" mt={1} mb={2}>
                  {item.children!.map((child) => {
                    const isChildCurrentlyActive = mode === child.id;
                    return (
                      <Flex
                        key={child.id}
                        align="center"
                        pl={12} // Indentação para parecer um submenu
                        pr={4}
                        py={2}
                        mx={2}
                        borderRadius="md"
                        cursor="pointer"
                        bg={
                          isChildCurrentlyActive
                            ? themeFx.navActiveBg
                            : "transparent"
                        }
                        color={
                          isChildCurrentlyActive
                            ? themeFx.navActiveColor
                            : themeFx.mutedText
                        }
                        fontWeight={isChildCurrentlyActive ? "bold" : "normal"}
                        fontSize="sm"
                        transition="all 0.2s"
                        _hover={{ bg: themeFx.navHoverBg }}
                        onClick={() => {
                          setMode(child.id);
                          onClose();
                        }}
                      >
                        {child.icon && (
                          <Icon as={child.icon} boxSize={4} mr={3} />
                        )}
                        <Text>{child.label}</Text>
                      </Flex>
                    );
                  })}
                </VStack>
              </Collapse>
            )}
          </Box>
        );
      })}
    </VStack>
  );

  return (
    <>
      {/* SIDEBAR DESKTOP */}
      <Box
        display={{ base: "none", md: "block" }}
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
        overflowY="auto"
      >
        <SidebarContent />
      </Box>

      {/* DRAWER MOBILE */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay display={{ base: "block", md: "none" }} />
        <DrawerContent
          bg={themeFx.sidebarBg}
          display={{ base: "block", md: "none" }}
        >
          <DrawerCloseButton color={themeFx.textColor} />
          <DrawerHeader
            borderBottomWidth="1px"
            borderColor={themeFx.headerBorder}
            color={themeFx.textColor}
          >
            <Flex align="center">
              <Image src="/EpiScope.png" alt="Logo" w="36px" mr={3} />
              <Text fontWeight={"light"}>EpiScope AI</Text>
            </Flex>
          </DrawerHeader>
          <DrawerBody pt={6} px={0}>
            <SidebarContent />
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
};
