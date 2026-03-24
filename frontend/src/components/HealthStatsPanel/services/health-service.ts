import api from "../../../middleware/api";

export const healthService = {
  // --- STRAVA ---
  getStravaAuthUrl: async () => {
    const response = await api.get("/strava/login");
    return response.data.auth_url;
  },
  getStravaStatus: async () => {
    const response = await api.get("/strava/status");
    return response.data.connected;
  },
  syncStrava: async () => {
    const response = await api.post("/strava/sync");
    return response.data;
  },
  getActivities: async () => {
    const response = await api.get("/strava/activities");
    return response.data;
  },

  // --- GOOGLE FIT ---
  getGoogleFitAuthUrl: async () => {
    const response = await api.get("/google_fit/login");
    return response.data.auth_url;
  },
  getGoogleFitStatus: async () => {
    const response = await api.get("/google_fit/status");
    return response.data.connected;
  },
  getGoogleFitMetrics: async () => {
    const response = await api.get("/google_fit/metrics");
    return response.data;
  },
  syncGoogleFit: async () => {
  const response = await api.post('/google_fit/sync'); // A rota de POST que criamos no controller
  return response.data;
},
};
