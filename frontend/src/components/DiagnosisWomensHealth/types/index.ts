// Tipagem do espectro do DeepFace (Vídeo)
export interface EmotionalDistribution {
  [emotion: string]: number;
}

// Tipagem dos biomarcadores do Librosa (Áudio)
export interface AudioFeatures {
  hesitation_ratio: number;
  mean_volume: number;
  pitch_variance: number;
  total_duration_sec: number;
}

// Interface unificada
export interface AnalysisData {
  source_type: "video" | "audio"; // 👈 A chave mágica para o UI saber o que renderizar
  emotional_blend: string;

  // Opcionais do Vídeo
  dominant_emotion?: string;
  emotion_distribution?: EmotionalDistribution;
  total_frames_analyzed?: number;

  // Opcionais do Áudio
  alerts?: string[];
  clinical_insights?: string[];
  raw_features?: AudioFeatures;
  transcription_snippet?: string;
}

export interface ItemsDetected {
  bleeding?: number;
  grasper?: number;
  hook?: number;
  ligasure?: number;
  scissor?: number;
  uterus?: number;
}

export interface LaparoscopyAnalysisResponse {
  status: string;
  analysis_id?: string;
  surgery_type?: string;
  total_analyzed_seconds?: number;
  items_detected?: ItemsDetected;
  bleeding_ratio?: number;
  clinical_alerts?: string[];
  maestro_recommendation?: string;
  annotated_frames?: string[];
  error?: string;
  details?: string;
}

export interface CycleProfilePayload {
  last_period_start: string; // Formato YYYY-MM-DD
  average_cycle_length: number;
  is_perimenopause: boolean;
}

export interface CyclePredictionResponse {
  status: string;
  message?: string;
  current_day_of_cycle?: number;
  estimated_phase?: string;
  next_period_prediction?: string;
  wearable_telemetry?: {
    heart_rate: number | null;
    source: string | null;
  };
  clinical_insights?: string[];
  maestro_recommendation?: string;
}

export type AnalysisStatus = "idle" | "analyzing" | "success" | "error";
