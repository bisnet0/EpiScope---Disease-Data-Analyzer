import React, { useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import { useAuth } from '../context/AuthContext';

interface ExperimentResult {
    accuracy: number;
    metrics: any;
    model_config: any;
}

export const ExperimentsPanel: React.FC = () => {
    const { token } = useAuth();
    const [modelType, setModelType] = useState('xgboost');
    
    // Parâmetros (Estado flexível)
    const [nEstimators, setNEstimators] = useState(100);
    const [maxDepth, setMaxDepth] = useState(6);
    const [learningRate, setLearningRate] = useState(0.1);

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ExperimentResult | null>(null);
    const [history, setHistory] = useState<any[]>([]); // Histórico da sessão atual

    const handleRunExperiment = async () => {
        setLoading(true);
        try {
            // Monta payload dinâmico
            const params: any = { max_depth: maxDepth };
            if (modelType !== 'decision_tree') params.n_estimators = nEstimators;
            if (modelType === 'xgboost') params.learning_rate = learningRate;

            const response = await fetch('http://localhost:5000/diagnose/experiment', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ model_type: modelType, params })
            });

            const data = await response.json();
            if (data.success) {
                setResult(data);
                // Adiciona ao histórico local do gráfico
                setHistory(prev => [...prev, {
                    name: `Exp #${prev.length + 1} (${modelType})`,
                    accuracy: (data.accuracy * 100).toFixed(1),
                    config: JSON.stringify(params)
                }]);
            }
        } catch (error) {
            console.error("Erro no experimento:", error);
            alert("Erro ao rodar experimento. Veja o console.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ marginTop: '30px', borderTop: '1px solid #444', paddingTop: '20px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                🧪 Laboratório de Hiperparâmetros <span style={{fontSize: '0.8rem', background: '#646cff', padding: '2px 8px', borderRadius: '4px'}}>MODO AVANÇADO</span>
            </h3>
            <p style={{ color: '#888', fontSize: '0.9rem', marginBottom: '20px' }}>
                Ajuste os parâmetros e treine modelos em tempo real usando uma amostra dos dados.
            </p>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                {/* Coluna 1: Controles */}
                <div style={{ flex: '1 1 300px', background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
                    <div className="form-group">
                        <label>Algoritmo:</label>
                        <select value={modelType} onChange={e => setModelType(e.target.value)}>
                            <option value="xgboost">XGBoost</option>
                            <option value="random_forest">Random Forest</option>
                            <option value="decision_tree">Decision Tree</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Profundidade Máxima (Max Depth): {maxDepth}</label>
                        <input type="range" min="1" max="20" value={maxDepth} onChange={e => setMaxDepth(Number(e.target.value))} />
                    </div>

                    {modelType !== 'decision_tree' && (
                        <div className="form-group">
                            <label>Nº Estimadores (Árvores): {nEstimators}</label>
                            <input type="range" min="10" max="500" step="10" value={nEstimators} onChange={e => setNEstimators(Number(e.target.value))} />
                        </div>
                    )}

                    {modelType === 'xgboost' && (
                        <div className="form-group">
                            <label>Taxa de Aprendizado (LR): {learningRate}</label>
                            <input type="range" min="0.01" max="1.0" step="0.01" value={learningRate} onChange={e => setLearningRate(Number(e.target.value))} />
                        </div>
                    )}

                    <button 
                        onClick={handleRunExperiment} 
                        disabled={loading}
                        style={{ width: '100%', marginTop: '10px', background: loading ? '#555' : '#2ecc71', color: '#000', fontWeight: 'bold' }}
                    >
                        {loading ? 'Treinando...' : '🧪 Rodar Experimento'}
                    </button>
                </div>

                {/* Coluna 2: Resultados */}
                <div style={{ flex: '2 1 400px', background: '#1e1e1e', padding: '20px', borderRadius: '8px', minHeight: '300px' }}>
                    {history.length > 0 ? (
                        <>
                            <h4>Evolução dos Experimentos</h4>
                            <div style={{ width: '100%', height: 250 }}>
                                <ResponsiveContainer>
                                    <BarChart data={history}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                        <XAxis dataKey="name" stroke="#aaa" />
                                        <YAxis domain={[0, 100]} unit="%" stroke="#aaa" />
                                        <Tooltip contentStyle={{ background: '#333' }} />
                                        <ReferenceLine y={70} label="Meta (70%)" stroke="red" strokeDasharray="3 3" />
                                        <Bar dataKey="accuracy" name="Acurácia (%)" fill="#82ca9d">
                                            {history.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={index === history.length - 1 ? '#2ecc71' : '#555'} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                            {result && (
                                <div style={{ marginTop: '10px', padding: '10px', background: '#333', borderRadius: '4px' }}>
                                    <strong>Último Resultado:</strong> {(result.accuracy * 100).toFixed(2)}% de Acurácia.
                                    <br />
                                    <small style={{ color: '#ccc' }}>Params: {JSON.stringify(result.model_config)}</small>
                                </div>
                            )}
                        </>
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#666' }}>
                            <p>Configure os parâmetros e rode o primeiro teste.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};