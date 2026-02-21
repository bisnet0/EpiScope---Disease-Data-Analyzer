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

export interface GlaucomaGARunParams {
  model_type: string;
  generations: number;
  population_size: number;
  mutation_rate: number;
  crossover_rate: number;
}