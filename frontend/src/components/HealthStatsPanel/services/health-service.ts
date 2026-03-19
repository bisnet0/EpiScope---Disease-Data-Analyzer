import api from "../../../middleware/api";

export const healthService = {
  getStravaAuthUrl: async () => {
    const response = await api.get('/strava/login');
    return response.data.auth_url;
  },

  getConnectionStatus: async () => {
    const response = await api.get('/strava/status');
    return response.data.connected;
  },

  // Novo: Dispara o worker de sincronização no backend
  syncActivities: async () => {
    const response = await api.post('/strava/sync');
    return response.data;
  },

  getActivities: async () => {
    const response = await api.get('/strava/activities');
    return response.data;
  }
};