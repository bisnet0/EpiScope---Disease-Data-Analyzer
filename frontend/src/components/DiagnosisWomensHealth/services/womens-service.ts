import api from "../../../middleware/api";
import {
  type LaparoscopyAnalysisResponse,
  type CyclePredictionResponse,
  type CycleProfilePayload,
} from "../types";

export const womensService = {
  analyzeVideo: async (file: File, type: string) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("consultation_type", type);
    return api.post("/womens-health/analyze-video", formData);
  },

  analyzeAudio: async (file: Blob, type: string) => {
    const formData = new FormData();
    formData.append("file", file, "audio.wav");
    formData.append("consultation_type", type);
    return api.post("/womens-health/analyze-audio", formData);
  },

  getIntegratedReport: async (type: string) => {
    return api.get(`/womens-health/get-report?consultation_type=${type}`);
  },

  analyzeLaparoscopyVideo: async (
    file: File,
  ): Promise<LaparoscopyAnalysisResponse> => {
    await pingAndRefreshToken();

    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/womens-health/analyze-surgery", formData);
    return response.data;
  },

  updateCycleProfile: async (data: CycleProfilePayload) => {
    const response = await api.post("/womens-health/cycle-profile", data);
    return response.data;
  },

  getCyclePrediction: async (): Promise<CyclePredictionResponse> => {
    const response = await api.get("/womens-health/cycle-prediction");
    return response.data;
  },
};

export const updateWarningPreference = async (dontShowAgain: boolean) => {
  return api.patch("/users/preferences", {
    hide_surgery_warning: dontShowAgain,
  });
};

const pingAndRefreshToken = async () => {
  try {
    await api.get("/patients/diagnose/history");
  } catch (error) {
    console.warn("Falha ao pingar revalidação de token.", error);
  }
};
