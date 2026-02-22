import React from "react";
import { Flex, Heading, HStack, Text, Select, IconButton, Icon } from "@chakra-ui/react";
import { Activity, Filter, ArrowRepeat } from "react-bootstrap-icons";
import { useDashboardThemeFx } from "../styles/theme-fx";
import { type DashboardHeaderProps } from "../types";


export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  periodFilter, setPeriodFilter, modelFilter, setModelFilter, onRefresh, loading
}) => {
  const themeFx = useDashboardThemeFx();

  return (
    <Flex justify="space-between" align="center" mb={8} wrap="wrap" gap={4}>
      <Heading size="lg" display="flex" alignItems="center" gap={3} color={themeFx.textColor}>
        <Icon as={Activity} color={themeFx.accentColor} /> Analytics em Tempo Real
      </Heading>

      <Flex 
        bg={themeFx.filterPanelBg} 
        p={2} 
        borderRadius="xl" 
        border="1px solid" 
        borderColor={themeFx.cardBorder}
        boxShadow="sm"
        align="center"
        gap={3}
        wrap="wrap"
      >
        <HStack color={themeFx.mutedText} px={2} spacing={2}>
          <Icon as={Filter} />
          <Text fontSize="sm" fontWeight="bold">Filtros:</Text>
        </HStack>

        <Select 
          value={periodFilter} 
          onChange={(e) => setPeriodFilter(e.target.value)} 
          variant="filled" 
          bg={themeFx.inputBg}
          _hover={{ bg: themeFx.inputBg }}
          _focus={{ bg: themeFx.inputBg, borderColor: themeFx.accentColor }}
          size="sm"
          borderRadius="md"
          w="auto"
        >
          <option value="all">📅 Todo o Período</option>
          <option value="24h">🕒 Últimas 24 Horas</option>
          <option value="7d">📅 Últimos 7 Dias</option>
          <option value="30d">📅 Últimos 30 Dias</option>
        </Select>

        <Select 
          value={modelFilter} 
          onChange={(e) => setModelFilter(e.target.value)} 
          variant="filled" 
          bg={themeFx.inputBg}
          _hover={{ bg: themeFx.inputBg }}
          _focus={{ bg: themeFx.inputBg, borderColor: themeFx.accentColor }}
          size="sm"
          borderRadius="md"
          w="auto"
        >
          <option value="all">🤖 Todos os Modelos</option>
          <option value="xgboost">🚀 XGBoost</option>
          <option value="random_forest">🌲 Random Forest</option>
          <option value="decision_tree">🌳 Decision Tree</option>
          <option value="glaucoma">🚀🌲 Híbrido</option>
        </Select>

        <IconButton
          aria-label="Atualizar Agora"
          icon={<ArrowRepeat size={20} />}
          onClick={onRefresh}
          isLoading={loading}
          variant="ghost"
          colorScheme="blue"
          size="sm"
          isRound
        />
      </Flex>
    </Flex>
  );
};