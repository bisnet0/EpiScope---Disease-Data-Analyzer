import React, { useState } from 'react';
import {
    BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine, Legend
} from 'recharts';
import api from '../services/api';
import Toast from './Toast'; 

interface EvolutionStep {
    generation: number;
    best_accuracy: number;
    avg_accuracy: number;
}

interface ToastState {
    type: 'success' | 'error' | 'info';
    title?: string;
    message: string;
}

export const GlaucomaExperimentsPanel: React.FC = () => {
    const [modelType, setModelType] = useState('xgboost');
    
    // Parâmetros do Classificador Final (Transfer Learning)
    const [nEstimators, setNEstimators] = useState(100);
    const [maxDepth, setMaxDepth] = useState(6);
    const [learningRate, setLearningRate] = useState(0.1);

    const [loading, setLoading] = useState(false);
    const [evolutionHistory, setEvolutionHistory] = useState<EvolutionStep[]>([]);
    const [toast, setToast] = useState<ToastState | null>(null);
    
    const closeToast = () => setToast(null);

    // RODA A EVOLUÇÃO (Rota Específica de Glaucoma)
    const handleRunEvolution = async () => {
        setLoading(true);
        setEvolutionHistory([]); 

        try {
            // Rota nova do Glaucoma
            const response = await api.post('/diagnose/glaucoma/optimize-ga', {
                model_type: modelType
            });
            
            const data = response.data;
            if (data.success) {
                setEvolutionHistory(data.history.map((h: any) => ({
                    generation: h.generation,
                    best_accuracy: parseFloat((h.best_accuracy * 100).toFixed(2)),
                    avg_accuracy: parseFloat((h.avg_accuracy * 100).toFixed(2))
                })));
                
                // Aplica melhor config
                const params = data.best_individual.params;
                if (params.n_estimators) setNEstimators(Number(params.n_estimators));
                if (params.max_depth) setMaxDepth(Number(params.max_depth));
                if (params.learning_rate) setLearningRate(Number(params.learning_rate));
                
                setToast({
                    type: 'success',
                    title: 'Transfer Learning Otimizado!',
                    message: `Acurácia do classificador atingiu ${(data.best_individual.accuracy * 100).toFixed(2)}%.`
                });
            }
        } catch (error: any) {
            console.error(error);
            setToast({ type: 'error', message: 'Erro na evolução.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ marginTop: '30px', borderTop: '1px solid #444', paddingTop: '20px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#e91e63' }}>
                👁️ Laboratório de Visão Computacional <span style={{ fontSize: '0.8rem', background: '#333', padding: '2px 8px', borderRadius: '4px', color: '#fff' }}>HÍBRIDO</span>
            </h3>
            
            <p style={{ color: '#aaa', fontSize: '0.9rem', marginBottom: '20px' }}>
                Otimize o classificador final (Top-Layer) que processa as características extraídas pela CNN.
            </p>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                
                {/* --- CONTROLES --- */}
                <div style={{ flex: '1 1 300px', background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
                    <div className="form-group">
                        <label>Classificador Final (Head):</label>
                        <select value={modelType} onChange={e => setModelType(e.target.value)}>
                            <option value="xgboost">XGBoost (Gradient Boosting)</option>
                            <option value="random_forest">Random Forest</option>
                            <option value="decision_tree">Decision Tree</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Profundidade (Max Depth): {maxDepth}</label>
                        <input type="range" min="1" max="50" value={maxDepth} onChange={e => setMaxDepth(Number(e.target.value))} />
                    </div>

                    {modelType !== 'decision_tree' && (
                        <div className="form-group">
                            <label>Estimadores: {nEstimators}</label>
                            <input type="range" min="10" max="1000" step="10" value={nEstimators} onChange={e => setNEstimators(Number(e.target.value))} />
                        </div>
                    )}

                    <button
                        onClick={handleRunEvolution}
                        disabled={loading}
                        style={{ 
                            width: '100%', marginTop: '20px', 
                            background: loading ? '#555' : 'linear-gradient(45deg, #e91e63, #9b59b6)', 
                            color: '#fff', fontWeight: 'bold', padding: '12px', border: 'none', borderRadius: '6px', cursor: 'pointer' 
                        }}
                    >
                        {loading ? '🧬 Evoluindo Rede...' : '🧬 Iniciar Algoritmo Genético'}
                    </button>
                </div>

                {/* --- GRÁFICO --- */}
                <div style={{ flex: '2 1 400px', background: '#1e1e1e', padding: '20px', borderRadius: '8px', minHeight: '350px' }}>
                    {evolutionHistory.length > 0 ? (
                        <div style={{ width: '100%', height: 300 }}>
                            <h4 style={{textAlign: 'center', marginBottom: '10px'}}>Evolução da Acurácia (CNN + {modelType.toUpperCase()})</h4>
                            <ResponsiveContainer>
                                <LineChart data={evolutionHistory}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                    <XAxis dataKey="generation" label={{ value: 'Geração', position: 'insideBottom', offset: -5 }} stroke="#aaa" />
                                    <YAxis domain={['auto', 'auto']} unit="%" stroke="#aaa" />
                                    <Tooltip contentStyle={{ background: '#333' }} />
                                    <Legend verticalAlign="top" />
                                    <Line type="monotone" dataKey="best_accuracy" name="Melhor Config" stroke="#e91e63" strokeWidth={3} dot={{r: 4}} />
                                    <Line type="monotone" dataKey="avg_accuracy" name="Média População" stroke="#8884d8" strokeDasharray="5 5" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#666', flexDirection: 'column' }}>
                            <p>O gráfico de evolução aparecerá aqui.</p>
                        </div>
                    )}
                </div>
            </div>
            
            {toast && <Toast type={toast.type} message={toast.message} onClose={closeToast} title={toast.title} />}
        </div>
    );
};