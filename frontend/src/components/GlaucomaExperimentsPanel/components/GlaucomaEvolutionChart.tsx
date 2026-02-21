import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { EvolutionStep } from '../types';

interface Props {
  history: EvolutionStep[];
  modelType: string;
}

export const GlaucomaEvolutionChart: React.FC<Props> = ({ history, modelType }) => {
  return (
    <div style={{ flex: '2 1 400px', background: '#1e1e1e', padding: '20px', borderRadius: '8px', minHeight: '350px' }}>
      {history.length > 0 ? (
        <div style={{ width: '100%', height: 300 }}>
          <h4 style={{ textAlign: 'center', marginBottom: '10px' }}>
            Evolução da Acurácia (CNN + {modelType.toUpperCase()})
          </h4>
          <ResponsiveContainer>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="generation" label={{ value: 'Geração', position: 'insideBottom', offset: -5 }} stroke="#aaa" />
              <YAxis domain={['auto', 'auto']} unit="%" stroke="#aaa" />
              <Tooltip contentStyle={{ background: '#333' }} />
              <Legend verticalAlign="top" />
              <Line type="monotone" dataKey="best_accuracy" name="Melhor Config" stroke="#e91e63" strokeWidth={3} dot={{ r: 4 }} />
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
  );
};