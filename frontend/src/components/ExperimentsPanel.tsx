import React, { useState } from 'react';
import {
    BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine, Legend
} from 'recharts';
import api from '../services/api';
// Se não tiver Toast, remova.
import Toast from './Toast';

interface ExperimentResult {
    accuracy: number;
    metrics: any;
    model_config: any;
}

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

export const ExperimentsPanel: React.FC = () => {
    const [modelType, setModelType] = useState('xgboost');

    // Parâmetros (Estado flexível)
    const [nEstimators, setNEstimators] = useState(100);
    const [maxDepth, setMaxDepth] = useState(6);
    const [learningRate, setLearningRate] = useState(0.1);

    const [loading, setLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState('');

    // Resultados Manuais vs Evolutivos
    const [manualHistory, setManualHistory] = useState<any[]>([]);
    const [evolutionHistory, setEvolutionHistory] = useState<EvolutionStep[]>([]);
    const [viewMode, setViewMode] = useState<'manual' | 'evolution'>('manual');

    const [result, setResult] = useState<ExperimentResult | null>(null);
    const [toast, setToast] = useState<ToastState | null>(null);

    const closeToast = () => setToast(null);

    // 1. EXPERIMENTO MANUAL (Ocorre ao clicar em "Rodar Experimento")
    const handleRunExperiment = async () => {
        setLoading(true);
        setLoadingMessage('Treinando modelo individual...');
        try {
            const params: any = { max_depth: maxDepth };
            if (modelType !== 'decision_tree') params.n_estimators = nEstimators;
            if (modelType === 'xgboost') params.learning_rate = learningRate;

            const response = await api.post('/diagnose/experiment', {
                model_type: modelType,
                params
            });

            const data = response.data;

            if (data.success) {
                setResult(data);
                setManualHistory(prev => [...prev, {
                    name: `Exp #${prev.length + 1}`,
                    accuracy: (data.accuracy * 100).toFixed(1),
                    config: JSON.stringify(params),
                    model: modelType
                }]);
                setViewMode('manual');
            }
        } catch (error: any) {
            setToast({ type: 'error', message: error.response?.data?.error || 'Erro ao rodar experimento.' });
        } finally {
            setLoading(false);
        }
    };

    // 2. AI ADVISOR (Consulta histórico global)
    const handleSuggestParams = async () => {
        setLoading(true);
        setLoadingMessage('Consultando o Oráculo...');
        try {
            const response = await api.get('/diagnose/advisor');
            const data = response.data;

            if (data.success && data.suggestion) {
                applyParams(data.suggestion.model_type, data.suggestion.params);
                setToast({
                    type: 'success',
                    title: 'Sugestão Aplicada',
                    message: `Melhor config histórica (${(data.suggestion.accuracy * 100).toFixed(1)}%) carregada!`
                });
            }
        } catch (error: any) {
            setToast({ type: 'error', message: 'Erro ao consultar Advisor.' });
        } finally {
            setLoading(false);
        }
    };

    // 3. ALGORITMO GENÉTICO (Novo!)
    const handleRunEvolution = async () => {
        setLoading(true);
        setLoadingMessage(`🧬 Evoluindo ${modelType.toUpperCase()} (Isso leva uns segundos)...`);
        setEvolutionHistory([]); // Limpa gráfico anterior

        try {
            const response = await api.post('/diagnose/optimize-ga', {
                model_type: modelType
            });

            const data = response.data;
            if (data.success) {
                // Atualiza Gráfico de Evolução
                setEvolutionHistory(data.history.map((h: any) => ({
                    generation: h.generation,
                    best_accuracy: parseFloat((h.best_accuracy * 100).toFixed(2)),
                    avg_accuracy: parseFloat((h.avg_accuracy * 100).toFixed(2))
                })));

                // Aplica o "Indivíduo Alfa" nos sliders
                applyParams(modelType, data.best_individual.params);

                setViewMode('evolution');
                setToast({
                    type: 'success',
                    title: 'Evolução Concluída! 🧬',
                    message: `Acurácia subiu para ${(data.best_individual.accuracy * 100).toFixed(2)}%. Parâmetros aplicados.`
                });
            }
        } catch (error: any) {
            console.error(error);
            setToast({ type: 'error', message: 'Erro na evolução genética.' });
        } finally {
            setLoading(false);
        }
    };

    // Helper para preencher sliders
    const applyParams = (type: string, params: any) => {
        setModelType(type);
        if (params.n_estimators) setNEstimators(Number(params.n_estimators));
        if (params.max_depth) setMaxDepth(Number(params.max_depth));
        if (params.learning_rate) setLearningRate(Number(params.learning_rate));
    };

    return (
        <div style={{ marginTop: '30px', borderTop: '1px solid #444', paddingTop: '20px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                🧪 Laboratório de Hiperparâmetros <span style={{ fontSize: '0.8rem', background: '#646cff', padding: '2px 8px', borderRadius: '4px' }}>MODO AVANÇADO</span>
            </h3>

            <p style={{ color: '#888', fontSize: '0.9rem', marginBottom: '20px' }}>
                Utilize Algoritmos Genéticos para encontrar a configuração perfeita ou teste manualmente.
            </p>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>

                {/* --- COLUNA 1: CONTROLES --- */}
                <div style={{ flex: '1 1 300px', background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>

                    {/* Botões de IA */}
                    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                        <button
                            onClick={handleSuggestParams}
                            disabled={loading}
                            title="Buscar melhor histórico"
                            style={{ flex: 1, background: 'linear-gradient(-45deg, #101bec80, #1db731e5)', border: '1px solid #555', color: '#fff', padding: '10px', cursor: 'pointer', borderRadius: '6px' }}
                        >
                            🔮 Oráculo
                        </button>
                        <button
                            onClick={handleRunEvolution}
                            disabled={loading}
                            title="Rodar Algoritmo Genético"
                            style={{ flex: 1, background: 'linear-gradient(45deg, #8e44ad, #c0392b)', border: 'none', color: '#fff', padding: '10px', cursor: 'pointer', borderRadius: '6px', fontWeight: 'bold' }}
                        >
                            🧬 Evoluir
                        </button>
                    </div>

                    {/* Form Manual */}
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
                        <input type="range" min="1" max="50" value={maxDepth} onChange={e => setMaxDepth(Number(e.target.value))} />
                    </div>

                    {modelType !== 'decision_tree' && (
                        <div className="form-group">
                            <label>Nº Estimadores (Árvores): {nEstimators}</label>
                            <input type="range" min="10" max="1000" step="10" value={nEstimators} onChange={e => setNEstimators(Number(e.target.value))} />
                        </div>
                    )}

                    {modelType === 'xgboost' && (
                        <div className="form-group">
                            <label>Taxa de Aprendizado (LR): {learningRate}</label>
                            <input type="range" min="0.001" max="1.0" step="0.001" value={learningRate} onChange={e => setLearningRate(Number(e.target.value))} />
                        </div>
                    )}

                    <button
                        onClick={handleRunExperiment}
                        disabled={loading}
                        style={{ width: '100%', marginTop: '15px', background: loading ? '#555' : '#2ecc71', color: '#000', fontWeight: 'bold', padding: '12px', border: 'none', borderRadius: '6px', cursor: loading ? 'wait' : 'pointer' }}
                    >
                        {loading ? loadingMessage || 'Processando...' : '🧪 Rodar Teste Único'}
                    </button>
                </div>

                {/* --- COLUNA 2: GRÁFICOS --- */}
                <div style={{ flex: '2 1 400px', background: '#1e1e1e', padding: '20px', borderRadius: '8px', minHeight: '350px' }}>

                    {/* Toggle de Visualização */}
                    <div style={{ marginBottom: '15px', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
                        <button onClick={() => setViewMode('manual')} style={{ marginRight: '15px', background: 'none', border: 'none', color: viewMode === 'manual' ? '#2ecc71' : '#666', cursor: 'pointer', fontWeight: 'bold' }}>
                            📊 Histórico Manual
                        </button>
                        <button onClick={() => setViewMode('evolution')} style={{ background: 'none', border: 'none', color: viewMode === 'evolution' ? '#8e44ad' : '#666', cursor: 'pointer', fontWeight: 'bold' }}>
                            🧬 Linha do Tempo Evolutiva
                        </button>
                    </div>

                    {/* GRÁFICO MANUAL (BARRAS) */}
                    {viewMode === 'manual' && manualHistory.length > 0 && (
                        <div style={{ width: '100%', height: 280 }}>
                            <ResponsiveContainer>
                                <BarChart data={manualHistory}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                    <XAxis dataKey="name" stroke="#aaa" fontSize={12} />
                                    <YAxis domain={[0, 100]} unit="%" stroke="#aaa" />
                                    <Tooltip contentStyle={{ background: '#333' }} />
                                    <ReferenceLine y={70} label="Meta (70%)" stroke="red" strokeDasharray="3 3" />
                                    <Bar dataKey="accuracy" name="Acurácia" fill="#82ca9d">
                                        {manualHistory.map((e, i) => (
                                            <Cell key={i} fill={e.model === 'xgboost' ? '#3498db' : '#2ecc71'} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    )}

                    {/* GRÁFICO EVOLUTIVO (LINHAS) */}
                    {viewMode === 'evolution' && evolutionHistory.length > 0 ? (
                        <div style={{ width: '100%', height: 280 }}>
                            <ResponsiveContainer>
                                <LineChart data={evolutionHistory}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                    <XAxis dataKey="generation" label={{ value: 'Geração', position: 'insideBottom', offset: -5 }} stroke="#aaa" />
                                    <YAxis domain={['auto', 'auto']} unit="%" stroke="#aaa" />
                                    <Tooltip contentStyle={{ background: '#333' }} />
                                    <Legend verticalAlign="top" height={36} />

                                    <Line type="monotone" dataKey="best_accuracy" name="Melhor Indivíduo" stroke="#8e44ad" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                                    <Line type="monotone" dataKey="avg_accuracy" name="Média da População" stroke="#8884d8" strokeDasharray="5 5" />
                                </LineChart>
                            </ResponsiveContainer>
                            <p style={{ textAlign: 'center', fontSize: '0.8rem', color: '#888', marginTop: '10px' }}>
                                O algoritmo seleciona os melhores modelos e cria "filhos" (Crossover/Mutação) a cada geração.
                            </p>
                        </div>
                    ) : (
                        viewMode === 'evolution' && (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: '#666', flexDirection: 'column' }}>
                                <p>Nenhuma evolução rodada ainda.</p>
                                <small>Clique em "🧬 Evoluir" para iniciar a seleção natural.</small>
                            </div>
                        )
                    )}

                    {/* STATUS VAZIO (MANUAL) */}
                    {viewMode === 'manual' && manualHistory.length === 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: '#666' }}>
                            <p>Configure os parâmetros e rode um teste.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Toast Component (Se existir) */}
            {toast && <Toast type={toast.type} message={toast.message} onClose={closeToast} title={toast.title} />}
        </div>
    );
};