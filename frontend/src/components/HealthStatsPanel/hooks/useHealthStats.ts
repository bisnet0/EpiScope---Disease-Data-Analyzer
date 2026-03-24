import { useState, useEffect } from "react";
import { healthService } from "../services/health-service";
import { type StravaActivity } from "../types";

export const useHealthStats = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnectedGoogle, setIsConnectedGoogle] = useState(false);
  const [activities, setActivities] = useState<StravaActivity[]>([]);
  const [googleMetrics, setGoogleMetrics] = useState({
    steps: 0,
    sleep_minutes: 0,
    resting_hr: 0,
    bpm_min: 0,
    bpm_max: 0,
  });
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stravaConnected, googleConnected] = await Promise.all([
        healthService.getStravaStatus(),
        healthService.getGoogleFitStatus(),
      ]);

      setIsConnected(stravaConnected);
      setIsConnectedGoogle(googleConnected);

      if (stravaConnected) {
        const data = await healthService.getActivities();
        setActivities(data);
      }
      if (googleConnected) {
        const metrics = await healthService.getGoogleFitMetrics();
        setGoogleMetrics(metrics);
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
      await healthService.syncStrava();
      await healthService.syncGoogleFit();
      const [updatedActivities, updatedMetrics] = await Promise.all([
        healthService.getActivities(),
        healthService.getGoogleFitMetrics(),
      ]);

      setActivities(updatedActivities);
      setGoogleMetrics(updatedMetrics);
    } catch (err) {
      console.error("Erro na sincronização combinada", err);
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

  const handleConnectGoogle = async () => {
    try {
      const authUrl = await healthService.getGoogleFitAuthUrl();
      window.location.href = authUrl;
    } catch (err) {
      console.error("Erro ao iniciar login Google Fit", err);
    }
  };

  useEffect(() => {
    fetchData();
    if (window.location.search.includes("google_success=true")) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  return {
    isConnected,
    isConnectedGoogle,
    loading,
    handleConnect,
    handleConnectGoogle,
    activities,
    handleSync,
    isSyncing,
    googleMetrics,
  };
};
