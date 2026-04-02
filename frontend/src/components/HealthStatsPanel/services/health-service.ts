import api from "../../../middleware/api";

export const healthService = {
  // --- STRAVA ---
  getStravaAuthUrl: async () => {
    const response = await api.get("/integrations/strava/login");
    return response.data.auth_url;
  },
  getStravaStatus: async () => {
    const response = await api.get("/integrations/strava/status");
    return response.data.connected;
  },
  syncStrava: async () => {
    const response = await api.post("/integrations/strava/sync");
    return response.data;
  },
  getActivities: async () => {
    const response = await api.get("/integrations/strava/activities");
    return response.data;
  },

  // --- GOOGLE FIT ---
  getGoogleFitAuthUrl: async () => {
    const response = await api.get("/integrations/google-fit/login");
    return response.data.auth_url;
  },
  getGoogleFitStatus: async () => {
    const response = await api.get("/integrations/google-fit/status");
    return response.data.connected;
  },
  getGoogleFitMetrics: async () => {
    const response = await api.get("/integrations/google-fit/metrics");
    return response.data;
  },
  syncGoogleFit: async () => {
    const response = await api.post("/integrations/google-fit/sync");
    return response.data;
  },
  disconnectStrava: async () => {
    const response = await api.post("/integrations/strava/disconnect");
    return response.data;
  },
  disconnectGoogleFit: async () => {
    const response = await api.post("/integrations/google-fit/disconnect");
    return response.data;
  },
};