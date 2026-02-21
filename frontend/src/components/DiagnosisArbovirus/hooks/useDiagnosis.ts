import { useState, useMemo } from 'react';
import { fetchDiagnosis } from '../services/diagnosis-arbovirus-service';
import { ArbovirusApiResponse } from '../types';
import { DISEASE_COLORS, MODEL_COLORS } from '../utils/constants';

export const useDiagnosis = () => {
  const [textDescription, setTextDescription] = useState('');
  const [age, setAge] = useState<number | ''>('');
  const [sex, setSex] = useState('M');
  const [result, setResult] = useState<ArbovirusApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLab, setShowLab] = useState(false);

  const submitDiagnosis = async (event?: React.FormEvent) => {
    if (event) event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await fetchDiagnosis({
        text_description: textDescription,
        age: Number(age),
        sex,
      });
      setResult(data);
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || 'Erro ao processar solicitação.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const diseaseChartData = useMemo(() => {
    if (!result) return [];
    return Object.entries(result.analysis_details.probabilities)
      .map(([disease, prob]) => ({
        name: disease.charAt(0).toUpperCase() + disease.slice(1),
        probability: parseFloat((prob * 100).toFixed(1)),
        color: DISEASE_COLORS[disease] || '#cccccc'
      }))
      .sort((a, b) => b.probability - a.probability);
  }, [result]);

  const modelsChartData = useMemo(() => {
    if (!result || !result.analysis_details.comparative_stats) return [];
    return Object.entries(result.analysis_details.comparative_stats)
      .map(([modelName, stats]) => ({
        name: modelName.replace('_', ' ').toUpperCase(),
        confidence: parseFloat((stats.confidence * 100).toFixed(1)),
        key: modelName
      }))
      .sort((a, b) => b.confidence - a.confidence);
  }, [result]);

  return {
    form: { textDescription, setTextDescription, age, setAge, sex, setSex },
    state: { result, loading, error, showLab, setShowLab },
    actions: { submitDiagnosis },
    charts: { diseaseChartData, modelsChartData }
  };
};