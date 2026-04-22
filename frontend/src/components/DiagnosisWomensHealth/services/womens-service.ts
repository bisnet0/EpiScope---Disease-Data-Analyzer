import api from "../../../middleware/api";

export const womensService = {
  analyzeVideo: async (file: File, type: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('consultation_type', type);
    return api.post('/womens-health/analyze-video', formData);
  },

  analyzeAudio: async (file: Blob, type: string) => {
    const formData = new FormData();
    formData.append('file', file, 'audio.wav');
    formData.append('consultation_type', type);
    return api.post('/womens-health/analyze-audio', formData);
  },

  getIntegratedReport: async (type: string) => {
    return api.get(`/womens-health/get-report?consultation_type=${type}`);
  }
};