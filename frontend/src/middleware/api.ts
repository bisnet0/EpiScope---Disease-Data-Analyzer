import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
});
const refreshApi = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

let isRefreshing = false;


api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401) {

      if (originalRequest._retry) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await refreshApi.post('/auth/refresh');
        isRefreshing = false;

        return api(originalRequest);

      } catch (refreshError) {
        isRefreshing = false;

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
