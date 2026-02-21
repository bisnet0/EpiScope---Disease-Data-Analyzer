import React, { useState, useMemo, type ChangeEvent } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
} from "recharts";
import api from "../middleware/api"; // <--- Importando Axios

import { GlaucomaExperimentsPanel } from "./GlaucomaExperimentsPanel";

interface GlaucomaApiResponse {
  friendly_response: string;
  analysis_details: {
    probabilities: { [key: string]: number };
    predicted_class: string;
    confidence: number;
  };
}

const COLORS: { [key: string]: string } = {
  Normal: "#8884d8",
  Glaucomatous: "#e377c2",
};

export const DiagnosisGlaucomaForm: React.FC = () => {
  // Não precisamos mais de useAuth nem token
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

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!imageFile) {
      setError("Selecione uma imagem.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("image", imageFile);

    try {
      // SUBSTITUIÇÃO: api.post com formData
      // O Axios envia o cookie automaticamente e define o header multipart
      const response = await api.post("/diagnose-glaucoma", formData);

      // Sucesso (status 200)
      setResult(response.data);

    } catch (err: any) {
      // Tratamento de erro padronizado
      const msg = err.response?.data?.error || err.message || "Erro na análise da imagem.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    if (!result) return [];
    return Object.entries(result.analysis_details.probabilities)
      .map(([className, prob]) => ({
        name: className,
        probability: parseFloat((prob * 100).toFixed(1)),
        color: COLORS[className] || "#cccccc",
      }))
      .sort((a, b) => b.probability - a.probability);
  }, [result]);

  const formatResponse = (text: string) => text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br />");

  return (
    <div className="container">
      <form onSubmit={handleSubmit} className="form-section">
        <h2>2. Análise de Imagem (Glaucoma CNN)</h2>
        <div className="form-group">
          <label>Imagem do fundo do olho:</label>
          <input type="file" accept="image/*" onChange={handleImageChange} />
        </div>
        {previewUrl && (
          <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
            <img src={previewUrl} alt="Preview" style={{ maxWidth: "200px", borderRadius: "8px", border: "1px solid #444" }} />
          </div>
        )}
        <button type="submit" disabled={loading}>{loading ? "Analisando..." : "Enviar Imagem"}</button>
      </form>

      <div className="results-wrapper">
        {error && <div className="result-box error"><p>{error}</p></div>}
        {result && (
          <div className="result-box">
            <h3>👁️ Resultado da Visão Computacional</h3>
            <div dangerouslySetInnerHTML={{ __html: formatResponse(result.friendly_response) }} />

            <div style={{ height: 250, marginTop: '20px' }}>
              <ResponsiveContainer>
                <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis type="number" unit="%" domain={[0, 100]} stroke="#aaa" />
                  <YAxis type="category" dataKey="name" width={100} stroke="#aaa" />
                  <Tooltip contentStyle={{ backgroundColor: '#333' }} />
                  <Legend />
                  <Bar dataKey="probability" name="Confiança (%)">
                    {chartData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
      <div style={{ marginTop: '40px', textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => setShowLab(!showLab)}
          style={{ background: 'transparent', border: '1px solid #e91e63', color: '#e91e63', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
        >
          {showLab ? 'Fechar Lab' : '👁️ Abrir Lab de Visão Computacional (AG)'}
        </button>
      </div>

      {showLab && <GlaucomaExperimentsPanel />}
    </div>
  );
};