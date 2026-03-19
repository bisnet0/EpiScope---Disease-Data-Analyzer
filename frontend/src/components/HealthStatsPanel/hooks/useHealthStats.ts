import { useState, useEffect } from 'react';
import { healthService } from '../services/health-service';

export const useHealthStats = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  const checkStatus = async () => {
    try {
      const status = await healthService.getConnectionStatus();
      setIsConnected(status);
    } catch (err) {
      console.error("Erro ao checar status do Strava", err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      const authUrl = await healthService.getStravaAuthUrl();
      // Redireciona para o login laranja do Strava
      window.location.href = authUrl;
    } catch (err) {
      console.error("Erro ao iniciar login Strava", err);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  return { isConnected, loading, handleConnect };
};