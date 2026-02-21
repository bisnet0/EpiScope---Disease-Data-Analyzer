import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine, Legend } from 'recharts';
import { EvolutionStep, ManualHistoryItem } from '../types';

interface Props {
  viewMode: 'manual' | 'evolution';
  setViewMode: (mode: 'manual' | 'evolution') => void;
  manualHistory: ManualHistoryItem[];
  evolutionHistory: EvolutionStep[];
}

export const ChartsColumn: React.FC<Props> = ({ viewMode, setViewMode, manualHistory, evolutionHistory }) => {
  return (
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
  );
};