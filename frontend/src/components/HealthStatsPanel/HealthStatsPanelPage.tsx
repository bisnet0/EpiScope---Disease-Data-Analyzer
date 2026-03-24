import React from 'react';
import { Container, Box, Breadcrumb, BreadcrumbItem, BreadcrumbLink } from '@chakra-ui/react';
import HealthStatsPanel from './components/HealthStatsPanel';

const HealthStatsPanelPage: React.FC = () => {
  return (
    <Box w="full" maxW="1800px" mx="auto" pb={10}>
      <HealthStatsPanel />
    </Box>
  );
};

export default HealthStatsPanelPage;