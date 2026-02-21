import React, { useState, useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import api from '../middleware/api';
import { ExperimentsPanel } from './ExperimentsPanel';


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
            
            const response = await api.post('/diagnose', {
                text_description: textDescription,
                age: Number(age),
                sex: sex,
            });

            
            setResult(response.data);

        } catch (err: any) {
            
            const msg = err.response?.data?.error || err.message || 'Erro ao processar solicitação.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    const formatResponse = (text: string) => {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br />');
    };

    
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
                        style={{ background: 'transparent', border: '1px solid rgb(27, 132, 69)', color: '#aaa' }}
                    >
                        {showLab ? 'Fechar Laboratório' : '🔬 Abrir Laboratório de IA (Modo Avançado)'}
                    </button>
                </div>

                {/* Importante: O ExperimentsPanel TAMBÉM precisará ser atualizado para usar 'api' */}
                {showLab && <ExperimentsPanel />}
            </div>
        </div>
    );
};