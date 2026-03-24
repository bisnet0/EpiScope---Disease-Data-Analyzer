export interface XRayProbabilities {
  [key: string]: number;
}

export interface XRayAnalysisDetails {
  model_used: string;
  probabilities: XRayProbabilities;
  clinical_notes: string;
}

export interface XRayApiResponse {
  prediction: string;
  success: boolean;
  maestro_status?: string;
  needs_emergency?: boolean;
  analysis_details: {
    clinical_notes: string;
    model_used: string;
    probabilities: {
      Normal: number;
      Pneumonia: number;
    };
  };
}

export interface XRayState {
  previewUrl: string | null;
  result: XRayApiResponse | null;
  loading: boolean;
  error: string | null;
}
