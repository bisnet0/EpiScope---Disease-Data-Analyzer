import React, { useState, useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';

interface ApiResponse {
    friendly_response: string;
    analysis_details: {
        probabilities: {
            [key: string]: number;
        };
    };
}

const COLORS: { [key: string]: string } = {
    dengue: '#8884d8',
    chikungunya: '#82ca9d',
    zika: '#ffc658',
};

export const DiagnosisForm: React.FC = () => {
    const [textDescription, setTextDescription] = useState('');
    const [age, setAge] = useState<number | ''>('');
    const [sex, setSex] = useState('M');

    const [result, setResult] = useState<ApiResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('http://localhost:5000/diagnose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text_description: textDescription,
                    age: Number(age),
                    sex: sex,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const data: ApiResponse = await response.json();
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Ocorreu um erro ao processar a solicitação.');
        } finally {
            setIsLoading(false);
        }
    };

    const formatResponse = (text: string): string => {
        let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\n/g, '<br />');
        return html;
    };

    const chartData = useMemo(() => {
        if (!result) return [];

        return Object.entries(result.analysis_details.probabilities)
            .map(([disease, prob]) => ({
                name: disease.charAt(0).toUpperCase() + disease.slice(1),
                probability: parseFloat((prob * 100).toFixed(1)),
                color: COLORS[disease] || '#cccccc'
            }))
            .sort((a, b) => b.probability - a.probability);
    }, [result]);

    return (
        <div className="container">
            <form onSubmit={handleSubmit}>
                <h2>Relatar Sintomas</h2>
                <div className="form-group">
                    <label htmlFor="text_description">Descreva seus sintomas:</label>
                    <textarea
                        id="text_description"
                        value={textDescription}
                        onChange={(e) => setTextDescription(e.target.value)}
                        placeholder="Ex: Estou com febre alta e dor de cabeça há 3 dias..."
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="age">Idade:</label>
                    <input
                        type="number"
                        id="age"
                        value={age}
                        onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))}
                        min="0"
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="sex">Sexo:</label>
                    <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}>
                        <option value="M">Masculino</option>
                        <option value="F">Feminino</option>
                    </select>
                </div>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Analisando...' : 'Analisar Sintomas'}
                </button>
            </form>

            {error && <div className="result-box error"><p><strong>Erro:</strong> {error}</p></div>}

            {result && (
                <div className="result-box">
                    <h3>Análise do Assistente Virtual</h3>
                    <div dangerouslySetInnerHTML={{ __html: formatResponse(result.friendly_response) }} />

                    <h4>Probabilidades Estimadas (Gráfico)</h4>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <BarChart
                                data={chartData}
                                margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis unit="%" domain={[0, 100]} />
                                <Tooltip formatter={(value: number) => [`${value}%`, "Probabilidade"]} />
                                <Legend />
                                <Bar dataKey="probability" name="Probabilidade (%)">
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <h4>Probabilidades Estimadas (Lista)</h4>
                    <ul>
                        {chartData.map((item) => (
                            <li key={item.name}>{`${item.name}: ${item.probability}%`}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};