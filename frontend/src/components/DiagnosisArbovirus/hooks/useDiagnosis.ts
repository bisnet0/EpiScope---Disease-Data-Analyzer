import { useState, useMemo, useEffect } from "react";
import { fetchDiagnosis } from "../services/diagnosis-arbovirus-service";
import { type ArbovirusApiResponse, type AuditResult } from "../types";
import { DISEASE_COLORS, MODEL_COLORS } from "../utils/constants";
import { processAuditAndDecision } from "../../../services/diagnosis-service";
import { useToast } from "../../Toast/components/ToastContext";

export const useDiagnosis = () => {
  const [textDescription, setTextDescription] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [sex, setSex] = useState("M");
  const [result, setResult] = useState<ArbovirusApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLab, setShowLab] = useState(false);
  const [auditResult, setAuditResult] = useState<any>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { showToast } = useToast();

  const submitDiagnosis = async (event?: React.FormEvent) => {
    if (event) event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setAuditResult(null);

    try {
      const data = await fetchDiagnosis({
        text_description: textDescription,
        age: Number(age),
        sex,
      });
      setResult(data);
      const winner = data.analysis_details.winner_model || "unknown";
      const stats = data.analysis_details.comparative_stats;
      const technicalDiagnosis =
        stats && winner !== "unknown"
          ? stats[winner]?.diagnosis
          : "Não identificado";

      const modelName = winner.replace("_", " ");

      const rawDiagnosis = `SINTOMAS: ${textDescription} | Diagnóstico Técnico: Suspeita de ${technicalDiagnosis} via ${modelName} (Idade: ${age}, Sexo: ${sex})`;

      console.log("🚀 Enviando contexto real para o Maestro:", rawDiagnosis);

      const auditData = await processAuditAndDecision(rawDiagnosis);
      setAuditResult(auditData.data);
      setAuditResult(auditData.data as AuditResult);
    } catch (err: any) {
      const msg =
        err.response?.data?.error ||
        err.message ||
        "Erro ao processar solicitação.";
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
        color: DISEASE_COLORS[disease] || "#cccccc",
      }))
      .sort((a, b) => b.probability - a.probability);
  }, [result]);

  const modelsChartData = useMemo(() => {
    if (!result || !result.analysis_details.comparative_stats) return [];
    return Object.entries(result.analysis_details.comparative_stats)
      .map(([modelName, stats]) => ({
        name: modelName.replace("_", " ").toUpperCase(),
        confidence: parseFloat((stats.confidence * 100).toFixed(1)),
        key: modelName,
      }))
      .sort((a, b) => b.confidence - a.confidence);
  }, [result]);

  useEffect(() => {
    if (auditResult?.needs_emergency) {
      console.log("🚨 ALERTA GERAL: Acionando Agent de Emergência!");

      showToast({
        title: "Protocolo de Emergência!",
        message:
          "Maestro detectou alta severidade. O Agente de Emergência foi notificado.",
        type: "info",
        duration: 6000,
        isCloseable: true,
      });
      const event = new CustomEvent("openMaestroChat", {
        detail: { diagnosis: auditResult.diagnosis },
      });
      window.dispatchEvent(event);
      setIsChatOpen(true);
    }
  }, [auditResult, showToast]);

  return {
    form: { textDescription, setTextDescription, age, setAge, sex, setSex },
    state: {
      result,
      auditResult,
      loading,
      error,
      showLab,
      setShowLab,
      isChatOpen,
      setIsChatOpen,
    },
    actions: { submitDiagnosis },
    charts: { diseaseChartData, modelsChartData },
  };
};
