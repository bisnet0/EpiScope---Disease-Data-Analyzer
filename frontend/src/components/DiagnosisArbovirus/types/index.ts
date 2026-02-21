export interface ComparativeStat {
  diagnosis: string;
  confidence: number;
  full_probs: { [key: string]: number };
}

export interface ArbovirusApiResponse {
  friendly_response: string;
  analysis_details: {
    probabilities: { [key: string]: number };
    structured_symptoms: { [key: string]: boolean };
    diagnosis_id?: number;
    winner_model?: string;
    comparative_stats?: { [key: string]: ComparativeStat };
  };
}

export interface DiagnosisPayload {
  text_description: string;
  age: number;
  sex: string;
}