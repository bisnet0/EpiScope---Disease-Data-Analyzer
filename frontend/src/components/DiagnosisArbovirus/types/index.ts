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

export interface FormProps {
  textDescription: string;
  setTextDescription: (val: string) => void;
  age: number | '';
  setAge: (val: number | '') => void;
  sex: string;
  setSex: (val: string) => void;
  loading: boolean;
  onSubmit: (e: React.FormEvent) => void;
}

export interface AlgorithmsChartProps {
  data: any[];
  winnerModel?: string;
}
