import { ExperimentsPanel } from './ExperimentsPanel';
import React, { useState, useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import { useAuth } from '../context/AuthContext';

// Interfaces da Resposta
interface ComparativeStat {
    diagnosis: string;
    confidence: number;
    full_probs: { [key: string]: number };
}

interface ArbovirusApiResponse {
    friendly_response: string;
    analysis_details: {
        probabilities: { [key: string]: number };
        structured_symptoms: { [key: string]: boolean };
        diagnosis_id?: number;
        winner_model?: string;
        comparative_stats?: { [key: string]: ComparativeStat };
    };
}

// Cores
const COLORS: { [key: string]: string } = {
    dengue: '#8884d8',
    chikungunya: '#82ca9d',
    zika: '#ffc658',
};

const MODEL_COLORS: { [key: string]: string } = {
    xgboost_standard: '#3498db',
    xgboost_genetic: '#9b59b6',
    random_forest: '#2ecc71',
    decision_tree: '#e67e22',
    legacy_xgboost: '#95a5a6'
};

export const DiagnosisArbovirusForm: React.FC = () => {
    const { token } = useAuth();
    const [textDescription, setTextDescription] = useState('');
    const [age, setAge] = useState<number | ''>('');
    const [sex, setSex] = useState('M');
    const [result, setResult] = useState<ArbovirusApiResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showLab, setShowLab] = useState(false);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('http://localhost:5000/diagnose', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    text_description: textDescription,
                    age: Number(age),
                    sex: sex,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Erro HTTP: ${response.status}`);
            }
            const data: ArbovirusApiResponse = await response.json();
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Erro ao processar solicitação.');
        } finally {
            setLoading(false);
        }
    };

    const formatResponse = (text: string) => {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br />');
    };

    // Gráfico 1: Probabilidades da Doença (Modelo Vencedor)
    const diseaseChartData = useMemo(() => {
        if (!result) return [];
        return Object.entries(result.analysis_details.probabilities)
            .map(([disease, prob]) => ({
                name: disease.charAt(0).toUpperCase() + disease.slice(1),
                probability: parseFloat((prob * 100).toFixed(1)),
                color: COLORS[disease] || '#cccccc'
            }))
            .sort((a, b) => b.probability - a.probability);
    }, [result]);

    // Gráfico 2: Comparativo de Modelos
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

    return (
        <div className="container">
            <form onSubmit={handleSubmit} className="form-section">
                <h2>1. Análise Clínica (Arboviroses)</h2>
                <div className="form-group">
                    <label>Descreva seus sintomas:</label>
                    <textarea value={textDescription} onChange={(e) => setTextDescription(e.target.value)} required placeholder="Ex: Febre alta, dor atrás dos olhos..." />
                </div>
                <div className="form-group">
                    <label>Idade:</label>
                    <input type="number" value={age} onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))} min="0" required />
                </div>
                <div className="form-group">
                    <label>Sexo:</label>
                    <select value={sex} onChange={(e) => setSex(e.target.value)}>
                        <option value="M">Masculino</option>
                        <option value="F">Feminino</option>
                    </select>
                </div>
                <button type="submit" disabled={loading}>{loading ? 'Analisando...' : 'Rodar Diagnóstico'}</button>
            </form>

            <div className="results-wrapper">
                {error && <div className="result-box error"><p>{error}</p></div>}

                {result && (
                    <div className="result-box">
                        <h3>🤖 Resultado da Análise</h3>
                        <div dangerouslySetInnerHTML={{ __html: formatResponse(result.friendly_response) }} style={{ marginBottom: '2rem' }} />

                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
                            {/* Gráfico Doenças */}
                            <div style={{ flex: '1 1 400px', background: '#252525', padding: '15px', borderRadius: '8px' }}>
                                <h4 style={{ textAlign: 'center' }}>Probabilidades (Consenso)</h4>
                                <div style={{ height: 250 }}>
                                    <ResponsiveContainer>
                                        <BarChart data={diseaseChartData} layout="vertical" margin={{ left: 10, right: 30 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                            <XAxis type="number" unit="%" domain={[0, 100]} stroke="#aaa" />
                                            <YAxis type="category" dataKey="name" width={100} stroke="#aaa" />
                                            <Tooltip contentStyle={{ backgroundColor: '#333' }} />
                                            <Bar dataKey="probability" name="Confiança">
                                                {diseaseChartData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Gráfico Modelos */}
                            {modelsChartData.length > 0 && (
                                <div style={{ flex: '1 1 400px', background: '#252525', padding: '15px', borderRadius: '8px', border: '1px solid #444' }}>
                                    <h4 style={{ textAlign: 'center' }}>Comparativo de Algoritmos</h4>
                                    <div style={{ height: 250 }}>
                                        <ResponsiveContainer>
                                            <BarChart data={modelsChartData}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                                <XAxis dataKey="name" stroke="#aaa" fontSize={10} tickFormatter={(v) => v.split(' ')[0]} />
                                                <YAxis unit="%" domain={[0, 100]} stroke="#aaa" />
                                                <Tooltip contentStyle={{ backgroundColor: '#333' }} />
                                                <ReferenceLine y={50} stroke="#666" strokeDasharray="3 3" />
                                                <Bar dataKey="confidence" name="Certeza">
                                                    {modelsChartData.map((entry, index) => (
                                                        <Cell key={`cell-md-${index}`} fill={MODEL_COLORS[entry.key] || '#888'} />
                                                    ))}
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <p style={{ textAlign: 'center', fontSize: '0.8rem', color: '#888', marginTop: '10px' }}>
                                        Vencedor: <strong style={{ color: '#fff' }}>{result.analysis_details.winner_model?.toUpperCase().replace('_', ' ')}</strong>
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                <div style={{ marginTop: '40px', textAlign: 'center' }}>
                    <button
                        type="button"
                        onClick={() => setShowLab(!showLab)}
                        style={{ background: 'transparent', border: '1px solid #555', color: '#aaa' }}
                    >
                        {showLab ? 'Fechar Laboratório' : '🔬 Abrir Laboratório de IA (Modo Avançado)'}
                    </button>
                </div>

                {showLab && <ExperimentsPanel />}
            </div>
        </div>

    );
};