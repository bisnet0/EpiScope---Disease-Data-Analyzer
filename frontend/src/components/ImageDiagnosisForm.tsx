import React, { useState, useMemo, type ChangeEvent } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

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

export const ImageDiagnosisForm: React.FC = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [glaucomaResult, setGlaucomaResult] = useState<GlaucomaApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Formatação do texto
  const formatResponse = (text: string): string => {
    let html = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\n/g, "<br />");
    return html;
  };

  // Preview da imagem
  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setPreviewUrl(reader.result as string);
      reader.readAsDataURL(file);
      setError(null);
      setGlaucomaResult(null);
    }
  };

  // Envio do arquivo para o backend
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!imageFile) {
      setError("Por favor, selecione uma imagem antes de enviar.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setGlaucomaResult(null);

    const formData = new FormData();
    formData.append("image", imageFile);

    try {
      const response = await fetch("http://localhost:5000/diagnose-glaucoma", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `Erro ${response.status}`);
      }

      const data: GlaucomaApiResponse = await response.json();
      setGlaucomaResult(data);
    } catch (err: any) {
      setError(err.message || "Erro ao processar a análise da imagem.");
    } finally {
      setIsLoading(false);
    }
  };

  // Dados para o gráfico
  const glaucomaChartData = useMemo(() => {
    if (!glaucomaResult) return [];
    return Object.entries(glaucomaResult.analysis_details.probabilities)
      .map(([className, prob]) => ({
        name: className,
        probability: parseFloat((prob * 100).toFixed(1)),
        color: COLORS[className] || "#cccccc",
      }))
      .sort((a, b) => b.probability - a.probability);
  }, [glaucomaResult]);

  return (
    <div className="container">
      <form onSubmit={handleSubmit} className="form-section">
        <h2>Análise de Imagem de Glaucoma</h2>

        <div className="form-group">
          <label htmlFor="imageFile">Selecione a imagem do fundo do olho:</label>
          <input
            type="file"
            id="imageFile"
            accept="image/png, image/jpeg, image/jpg, image/bmp, image/tiff"
            onChange={handleImageChange}
          />
        </div>

        {previewUrl && (
          <div className="image-preview">
            <p>Pré-visualização:</p>
            <img
              src={previewUrl}
              alt="Preview do exame de fundo de olho"
              style={{
                maxWidth: "220px",
                maxHeight: "220px",
                marginTop: "10px",
                borderRadius: "8px",
              }}
            />
          </div>
        )}

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analisando imagem..." : "Enviar para análise"}
        </button>
      </form>
      {/* Coluna 2: Wrapper para os resultados */}
      <div className="results-wrapper">

      {error && (
        <div className="result-box error">
          <p><strong>Erro:</strong> {error}</p>
        </div>
      )}

      {glaucomaResult && (
        <div className="result-box">
          <h3>Resultado da Análise (Assistente Virtual)</h3>
          <div
            dangerouslySetInnerHTML={{
              __html: formatResponse(glaucomaResult.friendly_response),
            }}
          />
          <h4>Probabilidades Estimadas</h4>
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer>
              <BarChart
                data={glaucomaChartData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" unit="%" domain={[0, 100]} />
                <YAxis type="category" dataKey="name" width={100} />
                <Tooltip formatter={(value: number) => [`${value}%`, "Probabilidade"]} />
                <Legend />
                <Bar dataKey="probability" name="Probabilidade (%)">
                  {glaucomaChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p style={{ marginTop: "15px" }}>
            <strong>Predição:</strong> {glaucomaResult.analysis_details.predicted_class} <br />
            <strong>Confiança:</strong>{" "}
            {(glaucomaResult.analysis_details.confidence * 100).toFixed(1)}%
          </p>
        </div>
      )}
      </div>
    </div>
  );
};
