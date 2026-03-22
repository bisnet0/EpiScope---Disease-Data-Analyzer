import { useEffect, useState, type ChangeEvent } from "react";
import { fetchXRayDiagnosis } from "../services/xray-service";
import { type XRayApiResponse } from "../types";
import { useToast } from "../../Toast/components/ToastContext";

export const useXRay = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<XRayApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();

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
      setError("Selecione uma imagem de Raio-X pulmonar.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await fetchXRayDiagnosis(imageFile);
      setResult(data);
    } catch (err: any) {
      const msg =
        err.response?.data?.error ||
        err.message ||
        "Erro na análise da imagem.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    if (result?.needs_emergency === true) {
      const pneumoniaProb =
        result?.analysis_details?.probabilities?.Pneumonia || 0;

      showToast({
        title: "Alerta Pulmonar: Pneumonia Detectada",
        message:
          "O Maestro identificou infiltrado alveolar e iniciou protocolo de emergência.",
        type: "info",
      });

      const event = new CustomEvent("openMaestroChat", {
        detail: {
          diagnosis: `Pneumonia Detectada (${(pneumoniaProb * 100).toFixed(1)}% de probabilidade) via Raio-X Digital.`,
        },
      });
      window.dispatchEvent(event);
    }
  }, [result, showToast]);

  return {
    state: { previewUrl, result, loading, error },
    actions: { handleImageChange, submitDiagnosis },
  };

  return {
    state: { previewUrl, result, loading, error },
    actions: { handleImageChange, submitDiagnosis },
  };
};
