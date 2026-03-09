import type { ChangeEvent } from "react";

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

export interface GlaucomaInputFormProps {
  previewUrl: string | null;
  loading: boolean;
  onImageChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (event: React.FormEvent) => void;
}

export interface GlaucomaResultChartProps {
  result: GlaucomaApiResponse;
  chartData: ChartDataPoint[];
}
