import { useState } from 'react';
import { runGlaucomaGeneticOptimization } from '../services/glaucoma-experiments-service';
import { type EvolutionStep, type ToastState } from '../types';

export const useGlaucomaExperiments = () => {
  const [modelType, setModelType] = useState('xgboost');

  // Parâmetros do Classificador Final (Visualização)
  const [nEstimators, setNEstimators] = useState(100);
  const [maxDepth, setMaxDepth] = useState(6);
  const [learningRate, setLearningRate] = useState(0.1);

  // Parâmetros do GA
  const [generations, setGenerations] = useState(5);
  const [popSize, setPopSize] = useState(8);
  const [mutationRate, setMutationRate] = useState(0.1);
  const [showAdvancedGA, setShowAdvancedGA] = useState(false);

  // Estados de UI e Histórico
  const [loading, setLoading] = useState(false);
  const [evolutionHistory, setEvolutionHistory] = useState<EvolutionStep[]>([]);
  const [toast, setToast] = useState<ToastState | null>(null);

  const closeToast = () => setToast(null);

  const handleRunEvolution = async () => {
    setLoading(true);
    setEvolutionHistory([]);

    try {
      const data = await runGlaucomaGeneticOptimization({
        model_type: modelType,
        generations: generations,
        population_size: popSize,
        mutation_rate: mutationRate,
        crossover_rate: 0.7 
      });

      if (data.success) {
        setEvolutionHistory(data.history.map((h: any) => ({
          generation: h.generation,
          best_accuracy: parseFloat((h.best_accuracy * 100).toFixed(2)),
          avg_accuracy: parseFloat((h.avg_accuracy * 100).toFixed(2))
        })));

        const params = data.best_individual.params;
        if (params.n_estimators) setNEstimators(Number(params.n_estimators));
        if (params.max_depth) setMaxDepth(Number(params.max_depth));
        if (params.learning_rate) setLearningRate(Number(params.learning_rate));

        setToast({
          type: 'success',
          title: 'Transfer Learning Otimizado!',
          message: `Acurácia do classificador atingiu ${(data.best_individual.accuracy * 100).toFixed(2)}%.`
        });
      }
    } catch (error: any) {
      console.error(error);
      setToast({ type: 'error', message: 'Erro na evolução.' });
    } finally {
      setLoading(false);
    }
  };

  return {
    state: {
      modelType, nEstimators, maxDepth, learningRate,
      generations, popSize, mutationRate, showAdvancedGA,
      loading, evolutionHistory, toast
    },
    setters: {
      setModelType, setGenerations, setPopSize, setMutationRate, setShowAdvancedGA, closeToast
    },
    actions: { handleRunEvolution }
  };
};