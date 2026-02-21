import { useState } from 'react';
import { 
  runManualExperimentApi, 
  getAdvisorSuggestionApi, 
  runGeneticOptimizationApi 
} from '../services/experiments-service';
import { ExperimentResult, EvolutionStep, ToastState, ManualHistoryItem } from '../types';

export const useExperiments = () => {
  // Estados de Configuração do Modelo
  const [modelType, setModelType] = useState('xgboost');
  const [nEstimators, setNEstimators] = useState(100);
  const [maxDepth, setMaxDepth] = useState(6);
  const [learningRate, setLearningRate] = useState(0.1);

  // Estados de Configuração do GA
  const [generations, setGenerations] = useState(5);
  const [popSize, setPopSize] = useState(10);
  const [mutationRate, setMutationRate] = useState(0.1);
  const [showAdvancedGA, setShowAdvancedGA] = useState(false);

  // Estados de UI e Histórico
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [manualHistory, setManualHistory] = useState<ManualHistoryItem[]>([]);
  const [evolutionHistory, setEvolutionHistory] = useState<EvolutionStep[]>([]);
  const [viewMode, setViewMode] = useState<'manual' | 'evolution'>('manual');
  
  const [result, setResult] = useState<ExperimentResult | null>(null);
  const [toast, setToast] = useState<ToastState | null>(null);

  const closeToast = () => setToast(null);

  const applyParams = (type: string, params: any) => {
    setModelType(type);
    if (params.n_estimators) setNEstimators(Number(params.n_estimators));
    if (params.max_depth) setMaxDepth(Number(params.max_depth));
    if (params.learning_rate) setLearningRate(Number(params.learning_rate));
  };

  const handleRunExperiment = async () => {
    setLoading(true);
    setLoadingMessage('Treinando modelo individual...');
    try {
      const params: any = { max_depth: maxDepth };
      if (modelType !== 'decision_tree') params.n_estimators = nEstimators;
      if (modelType === 'xgboost') params.learning_rate = learningRate;

      const data = await runManualExperimentApi(modelType, params);

      if (data.success) {
        setResult(data);
        setManualHistory(prev => [...prev, {
          name: `Exp #${prev.length + 1}`,
          accuracy: (data.accuracy * 100).toFixed(1),
          config: JSON.stringify(params),
          model: modelType
        }]);
        setViewMode('manual');
      }
    } catch (error: any) {
      setToast({ type: 'error', message: error.response?.data?.error || 'Erro ao rodar experimento.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestParams = async () => {
    setLoading(true);
    setLoadingMessage('Consultando o Oráculo...');
    try {
      const data = await getAdvisorSuggestionApi();

      if (data.success && data.suggestion) {
        applyParams(data.suggestion.model_type, data.suggestion.params);
        setToast({
          type: 'success',
          title: 'Sugestão Aplicada',
          message: `Melhor config histórica (${(data.suggestion.accuracy * 100).toFixed(1)}%) carregada!`
        });
      }
    } catch (error: any) {
      setToast({ type: 'error', message: 'Erro ao consultar Advisor.' });
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvolution = async () => {
    setLoading(true);
    setLoadingMessage(`🧬 Evoluindo com Pop=${popSize}, Gen=${generations}...`);
    setEvolutionHistory([]);

    try {
      const data = await runGeneticOptimizationApi({
        model_type: modelType,
        generations,
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

        applyParams(modelType, data.best_individual.params);
        setViewMode('evolution');
        setToast({
          type: 'success',
          title: 'Evolução Concluída! 🧬',
          message: `Acurácia subiu para ${(data.best_individual.accuracy * 100).toFixed(2)}%. Parâmetros aplicados.`
        });
      }
    } catch (error: any) {
      console.error(error);
      setToast({ type: 'error', message: 'Erro na evolução genética.' });
    } finally {
      setLoading(false);
    }
  };

  return {
    state: {
      modelType, nEstimators, maxDepth, learningRate,
      generations, popSize, mutationRate, showAdvancedGA,
      loading, loadingMessage, manualHistory, evolutionHistory, viewMode, toast
    },
    setters: {
      setModelType, setNEstimators, setMaxDepth, setLearningRate,
      setGenerations, setPopSize, setMutationRate, setShowAdvancedGA,
      setViewMode, closeToast
    },
    actions: {
      handleRunExperiment, handleSuggestParams, handleRunEvolution
    }
  };
};