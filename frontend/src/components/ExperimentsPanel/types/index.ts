export interface ExperimentResult {
  accuracy: number;
  metrics: any;
  model_config: any;
}

export interface EvolutionStep {
  generation: number;
  best_accuracy: number;
  avg_accuracy: number;
}

export interface ToastState {
  type: 'success' | 'error' | 'info';
  title?: string;
  message: string;
}

export interface ManualHistoryItem {
  name: string;
  accuracy: string;
  config: string;
  model: string;
}

export interface GARunParams {
  model_type: string;
  generations: number;
  population_size: number;
  mutation_rate: number;
  crossover_rate: number;
}

export interface ControlsColumnProps {
  state: any;
  setters: any;
  actions: any;
}

export interface ChartsColumnProps {
  viewMode: 'manual' | 'evolution';
  setViewMode: (mode: 'manual' | 'evolution') => void;
  manualHistory: ManualHistoryItem[];
  evolutionHistory: EvolutionStep[];
}

