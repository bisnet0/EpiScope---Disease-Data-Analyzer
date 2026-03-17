
export interface XRayProbabilities {
  [key: string]: number;
}

export interface XRayAnalysisDetails {
  model_used: string;
  probabilities: XRayProbabilities;
  clinical_notes: string;
}

export interface XRayApiResponse {
  success: boolean;
  prediction: string;
  analysis_details: XRayAnalysisDetails;
}

export interface XRayState {
  previewUrl: string | null;
  result: XRayApiResponse | null;
  loading: boolean;
  error: string | null;
}