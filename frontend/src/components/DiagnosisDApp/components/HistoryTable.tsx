import React from "react";
import { 
  Box, Text, Badge, Button, Icon, Center, 
  Table, Thead, Tbody, Tr, Th, Td, TableContainer 
} from "@chakra-ui/react";
import { ClockHistory, CheckCircle, CloudUpload } from "react-bootstrap-icons";
import { type HistoryTableProps } from "../types";
import { formatTimeBR } from "../utils/formatters";
import { useDAppThemeFx } from "../styles/theme-fx";



export const HistoryTable: React.FC<HistoryTableProps> = ({ history, walletAddress, sendingId, onRegisterOnChain }) => {
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
    <TableContainer border="1px solid" borderColor={themeFx.tableBorder} borderRadius="xl" bg={themeFx.innerBg}>
      <Table variant="simple" size="md">
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
                  {new Date(item.date).toLocaleDateString("pt-BR")}
                  <Text as="span" fontSize="xs" color={themeFx.mutedText}>
                    {formatTimeBR(item.date)}
                  </Text>
                </Box>
              </Td>
              
              <Td>
                <Badge 
                  colorScheme={item.type === "Arbovirose" ? "blue" : "pink"} 
                  px={3} py={1} borderRadius="full"
                >
                  {item.type}
                </Badge>
              </Td>
              
              <Td>
                <Text color={themeFx.mutedText} fontSize="sm" maxW="250px" isTruncated>
                  {item.details}
                </Text>
              </Td>
              
              <Td isNumeric>
                {item.signature ? (
                  <Badge colorScheme="green" variant="outline" display="inline-flex" alignItems="center" gap={1} px={2} py={1}>
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
                    loadingText="Assinando..."
                    isDisabled={!walletAddress}
                  >
                    Registrar
                  </Button>
                )}
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};