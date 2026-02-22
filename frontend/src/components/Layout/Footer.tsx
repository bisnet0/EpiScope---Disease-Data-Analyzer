import React from 'react';
import { Flex, HStack, Text, Icon, Link } from '@chakra-ui/react';
import { Linkedin, Github, Globe } from 'react-bootstrap-icons';
import { useAppThemeFx } from '../../styles/app-theme-fx';

export const Footer: React.FC = () => {
  const themeFx = useAppThemeFx();

  return (
    <Flex 
      as="footer" 
      bg={themeFx.footerBg} 
      borderTop="1px solid" 
      borderColor={themeFx.headerBorder} 
      py={6} 
      px={{ base: 4, md: 8 }} 
      align="center" 
      justify="center" 
      direction="column" // 🚀 O segredo aqui: força o texto pra cima e os ícones pra baixo
      gap={3} // 🚀 Espaçamento vertical sutil entre o texto e as redes sociais
      mt="auto" 
    >
      <Text color={themeFx.mutedText} fontSize="sm" textAlign="center">
        Desenvolvido por <Text as="span" fontWeight="bold" color={themeFx.textColor}>Henrique Bisneto</Text>
      </Text>
      
      <HStack spacing={5} color={themeFx.mutedText}>
        <Link href="https://linkedin.com/in/bisnet0/" isExternal _hover={{ color: "blue.500", transform: "translateY(-2px)" }} transition="all 0.2s">
          <Icon as={Linkedin} boxSize={5} />
        </Link>
        <Link href="https://github.com/bisnet0" isExternal _hover={{ color: themeFx.textColor, transform: "translateY(-2px)" }} transition="all 0.2s">
          <Icon as={Github} boxSize={5} />
        </Link>
        <Link href="https://www.henriquebisneto.com.br/" isExternal _hover={{ color: "teal.500", transform: "translateY(-2px)" }} transition="all 0.2s">
          <Icon as={Globe} boxSize={5} />
        </Link>
      </HStack>
    </Flex>
  );
};