import React from "react";
import { 
  Box, Text, Badge, Button, Icon, Center, 
  Table, Thead, Tbody, Tr, Th, Td 
} from "@chakra-ui/react";
import { ClockHistory, CheckCircle, CloudUpload } from "react-bootstrap-icons";
import { type HistoryItem } from "../types";
import { formatTimeBR } from "../utils/formatters";
import { useDAppThemeFx } from "../styles/theme-fx";

interface Props {
  history: HistoryItem[];
  walletAddress: string | null;
  sendingId: number | null;
  onRegisterOnChain: (item: HistoryItem) => void;
}

export const HistoryTable: React.FC<Props> = ({ history, walletAddress, sendingId, onRegisterOnChain }) => {
  const themeFx = useDAppThemeFx();

  if (history.length === 0) {
    return (
      <Center flexDirection="column" p={10} bg={themeFx.innerBg} borderRadius="xl" border="1px solid" borderColor={themeFx.cardBorder}>
        <Text color={themeFx.textColor} fontWeight="bold">Nenhum diagnóstico encontrado.</Text>
        <Text color={themeFx.mutedText} fontSize="sm">Realize um diagnóstico nas outras abas primeiro.</Text>
      </Center>
    );
  }

  return (
    // 1. CAMADA EXTERNA (A Borda Bonitinha): Protege o design e corta os cantos
    <Box 
      w="100%" 
      border="1px solid" 
      borderColor={themeFx.tableBorder} 
      borderRadius="xl" 
      bg={themeFx.innerBg}
      overflow="hidden"
    >
      {/* 2. CAMADA DE ISOLAMENTO (A sua ideia!): Controla exclusivamente o scroll */}
      <Box 
        w="100%" 
        overflowX="auto" 
        css={{
          '&::-webkit-scrollbar': { height: '8px' },
          '&::-webkit-scrollbar-track': { background: 'transparent' },
          '&::-webkit-scrollbar-thumb': { background: 'rgba(150, 150, 150, 0.3)', borderRadius: '4px' },
          '&::-webkit-scrollbar-thumb:hover': { background: 'rgba(150, 150, 150, 0.5)' }
        }}
      >
        {/* 3. A TABELA: Ela acha que tem no mínimo 800px, então ela estica o quanto quiser aqui dentro */}
        <Table variant="simple" size={{ base: "sm", md: "md" }} minW="800px">
          <Thead bg={themeFx.tableHeaderBg}>
            <Tr>
              <Th color={themeFx.mutedText}>Data</Th>
              <Th color={themeFx.mutedText}>Tipo</Th>
              <Th color={themeFx.mutedText}>Resumo</Th>
              <Th isNumeric color={themeFx.mutedText}>Ação Blockchain</Th>
            </Tr>
          </Thead>
          <Tbody>
            {history.map((item) => (
              <Tr key={`${item.type}-${item.id}`} _hover={{ bg: "whiteAlpha.50" }}>
                <Td>
                  <Box display="flex" alignItems="center" gap={2} color={themeFx.textColor}>
                    <Icon as={ClockHistory} color={themeFx.mutedText} />
                    <Text as="span" fontSize={{ base: "xs", md: "sm" }}>
                      {new Date(item.date).toLocaleDateString("pt-BR")}
                    </Text>
                    <Text as="span" fontSize="xs" color={themeFx.mutedText}>
                      {formatTimeBR(item.date)}
                    </Text>
                  </Box>
                </Td>
                
                <Td>
                  <Badge 
                    colorScheme={item.type === "Arbovirose" ? "blue" : "pink"} 
                    px={2} py={1} borderRadius="full" fontSize={{ base: "2xs", md: "xs" }}
                  >
                    {item.type}
                  </Badge>
                </Td>
                
                {/* Aqui podemos deixar um tamanho generoso já que a tabela vai rolar de qualquer jeito */}
                <Td maxW="300px">
                  <Text color={themeFx.mutedText} fontSize={{ base: "xs", md: "sm" }} isTruncated>
                    {item.details}
                  </Text>
                </Td>
                
                <Td isNumeric>
                  {item.signature ? (
                    <Badge colorScheme="green" variant="outline" display="inline-flex" alignItems="center" gap={1} px={2} py={1} fontSize={{ base: "2xs", md: "xs" }}>
                      <Icon as={CheckCircle} /> Registrado
                    </Badge>
                  ) : (
                    <Button
                      size="sm"
                      variant={walletAddress ? "outline" : "ghost"}
                      colorScheme={walletAddress ? "blue" : "gray"}
                      leftIcon={<CloudUpload />}
                      onClick={() => onRegisterOnChain(item)}
                      isLoading={sendingId === item.id}
                      loadingText="Assinando"
                      isDisabled={!walletAddress}
                      fontSize={{ base: "xs", md: "sm" }}
                    >
                      Registrar
                    </Button>
                  )}
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </Box>
  );
};