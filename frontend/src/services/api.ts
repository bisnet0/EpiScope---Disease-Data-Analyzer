import axios from 'axios';

const api = axios.create({
  // Mudamos para bater no PROXY do Vite
  baseURL: '/api', 
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Se der 401 e não for retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // O proxy vai redirecionar isso para localhost:5000/auth/refresh
        await api.post('/auth/refresh');
        return api(originalRequest);
      } catch (refreshError) {
        // Se falhar, apenas rejeita. O AuthContext lida com o logout.
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;