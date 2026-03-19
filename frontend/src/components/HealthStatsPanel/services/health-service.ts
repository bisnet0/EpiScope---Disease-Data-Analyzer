import api from "../../../middleware/api";

export const healthService = {
  // Busca a URL de redirecionamento do Strava
  getStravaAuthUrl: async () => {
    const response = await api.get('/strava/login');
    return response.data.auth_url;
  },

  // Verifica se o usuário já tem o Strava conectado
  getConnectionStatus: async () => {
    const response = await api.get('/strava/status');
    return response.data.connected;
  },

  // (Futuro) Busca as atividades processadas
  getActivities: async () => {
    const response = await api.get('/strava/activities');
    return response.data;
  }
};