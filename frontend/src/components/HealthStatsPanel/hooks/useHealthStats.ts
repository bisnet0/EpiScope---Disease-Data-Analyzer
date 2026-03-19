import { useState, useEffect } from 'react';
import { healthService } from '../services/health-service';
import { type StravaActivity } from '../types';

export const useHealthStats = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [activities, setActivities] = useState<StravaActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const connected = await healthService.getConnectionStatus();
      setIsConnected(connected);

      if (connected) {
        // Busca o que já tem no banco
        const data = await healthService.getActivities();
        setActivities(data);
      }
    } catch (err) {
      console.error("Erro ao carregar dados do HealthStats", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await healthService.syncActivities();
      const updated = await healthService.getActivities();
      setActivities(updated);
    } catch (err) {
      console.error("Erro na sincronização", err);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleConnect = async () => {
    try {
      const authUrl = await healthService.getStravaAuthUrl();
      window.location.href = authUrl;
    } catch (err) {
      console.error("Erro ao iniciar login Strava", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { 
    isConnected, 
    loading, 
    handleConnect, 
    activities, 
    handleSync, 
    isSyncing 
  };
};