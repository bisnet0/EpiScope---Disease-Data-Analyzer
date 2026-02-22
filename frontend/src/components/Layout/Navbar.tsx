import React from 'react';
import { Flex, HStack, Image, Text, IconButton, Button, Icon } from '@chakra-ui/react';
import { Wallet2, PersonCircle } from 'react-bootstrap-icons';
import { VscSignOut } from 'react-icons/vsc';
import { FiMenu } from 'react-icons/fi'; // Icone do Hamburger
import ThemeToggle from '../Theme/ThemeToggle'; // Ajuste o caminho conforme seu projeto
import { useAppThemeFx } from '../../styles/app-theme-fx';
import { useAuth } from '../../context/AuthContext';

interface Props {
  onOpenSidebar: () => void;
}

export const Navbar: React.FC<Props> = ({ onOpenSidebar }) => {
  const themeFx = useAppThemeFx();
  const { user, walletAddress, connectWallet, signOut } = useAuth();

  return (
    <Flex
      as="header"
      position="fixed"
      top={0}
      left={0}
      w="100%"
      h="70px" // Altura fixa para referenciar depois
      zIndex={1000}
      bg={themeFx.headerBg}
      backdropFilter="blur(16px)"
      borderBottom="1px solid"
      borderColor={themeFx.headerBorder}
      boxShadow={themeFx.headerShadow}
      px={{ base: 4, md: 6 }}
      align="center"
      justify="space-between"
    >
      <HStack spacing={4}>
        {/* Ícone Menu Mobile (Escondido no Desktop) */}
        <IconButton
          display={{ base: 'flex', md: 'none' }}
          onClick={onOpenSidebar}
          variant="ghost"
          aria-label="Abrir menu"
          icon={<FiMenu size={24} color={themeFx.textColor} />}
        />
        
        {/* Logo */}
        <Flex align="center">
          <Image src="/EpiScope.png" alt="Logo" w="36px" mr={3} />
          <Text fontSize="xl" fontWeight="black" color={themeFx.textColor} letterSpacing="tight">
            EpiScope AI
          </Text>
        </Flex>
      </HStack>

      <HStack spacing={{ base: 2, md: 4 }}>
        <ThemeToggle />
        
        {walletAddress ? (
          <Button 
            size="sm" 
            variant="subtle" 
            colorScheme="green" 
            borderRadius="full" 
            leftIcon={<Icon as={Wallet2} />}
            display={{ base: "none", sm: "flex" }}
          >
            {walletAddress.substring(0, 6)}...{walletAddress.substring(38)}
          </Button>
        ) : (
          <Button 
            size="sm" 
            variant="outline" 
            colorScheme="orange" 
            borderRadius="full" 
            onClick={connectWallet}
            display={{ base: "none", sm: "flex" }}
          >
            Conectar Wallet
          </Button>
        )}

        <HStack color={themeFx.textColor} display={{ base: "none", md: "flex" }} bg="whiteAlpha.100" px={3} py={1.5} borderRadius="full">
          <Icon as={PersonCircle} boxSize={4} />
          <Text fontSize="sm" fontWeight="medium">{user?.username}</Text>
        </HStack>

        <IconButton
          aria-label="Sair"
          icon={<Icon as={VscSignOut} boxSize={5} />}
          variant="ghost"
          colorScheme="red"
          size="sm"
          isRound
          onClick={signOut}
          title="Sair"
        />
      </HStack>
    </Flex>
  );
};