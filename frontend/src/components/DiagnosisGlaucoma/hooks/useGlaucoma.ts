import { useState, useMemo, ChangeEvent } from "react";
import { fetchGlaucomaDiagnosis } from "../../../services/glaucoma-service";
import { GlaucomaApiResponse, ChartDataPoint } from "../types";
import { GLAUCOMA_COLORS } from "../utils/constants";

export const useGlaucoma = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<GlaucomaApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLab, setShowLab] = useState(false);

  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setPreviewUrl(reader.result as string);
      reader.readAsDataURL(file);
      setError(null);
      setResult(null);
    }
  };

  const submitDiagnosis = async (event?: React.FormEvent) => {
    if (event) event.preventDefault();
    if (!imageFile) {
      setError("Selecione uma imagem.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await fetchGlaucomaDiagnosis(imageFile);
      setResult(data);
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || "Erro na análise da imagem.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const chartData: ChartDataPoint[] = useMemo(() => {
    if (!result) return [];
    return Object.entries(result.analysis_details.probabilities)
      .map(([className, prob]) => ({
        name: className,
        probability: parseFloat((prob * 100).toFixed(1)),
        color: GLAUCOMA_COLORS[className] || "#cccccc",
      }))
      .sort((a, b) => b.probability - a.probability);
  }, [result]);

  return {
    state: { previewUrl, result, loading, error, showLab, setShowLab },
    actions: { handleImageChange, submitDiagnosis },
    charts: { chartData }
  };
};