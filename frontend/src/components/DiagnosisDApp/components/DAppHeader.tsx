import React from "react";
import { Flex, Heading, Button, Badge, Icon } from "@chakra-ui/react";
import { ShieldCheck } from "react-bootstrap-icons";
import { useDAppThemeFx } from "../styles/theme-fx";
import { type DAppHeaderProps } from "../types";

export const DAppHeader: React.FC<DAppHeaderProps> = ({ walletAddress, connectWallet }) => {
  const themeFx = useDAppThemeFx();

  return (
    <Flex 
      justify="space-between" 
      align="center" 
      mb={6} 
      wrap="wrap" 
      gap={4}
    >
      <Heading size="md" display="flex" alignItems="center" color={themeFx.textColor}>
        <Icon as={ShieldCheck} color={themeFx.brandColor} mr={3} w={6} h={6} />
        Cartesi DApp Ledger
      </Heading>

      {!walletAddress ? (
        <Button 
          onClick={connectWallet} 
          colorScheme="orange" 
          size="md"
        >
          🦊 Conectar MetaMask
        </Button>
      ) : (
        <Badge 
          colorScheme="green" 
          variant="subtle" 
          px={4} 
          py={2} 
          borderRadius="full" 
          fontSize="sm"
          border="1px solid"
          borderColor="green.400"
        >
          🟢 Wallet Conectada
        </Badge>
      )}
    </Flex>
  );
};