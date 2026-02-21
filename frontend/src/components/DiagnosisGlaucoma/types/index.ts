export interface GlaucomaApiResponse {
  friendly_response: string;
  analysis_details: {
    probabilities: { [key: string]: number };
    predicted_class: string;
    confidence: number;
  };
}

export interface ChartDataPoint {
  name: string;
  probability: number;
  color: string;
}