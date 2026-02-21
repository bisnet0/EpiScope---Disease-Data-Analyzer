import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { MODEL_COLORS } from '../../utils/constants';

interface Props {
  data: any[];
  winnerModel?: string;
}

export const AlgorithmsChart: React.FC<Props> = ({ data, winnerModel }) => {
  if (data.length === 0) return null;

  return (
    <div style={{ flex: '1 1 400px', background: '#252525', padding: '15px', borderRadius: '8px', border: '1px solid #444' }}>
      <h4 style={{ textAlign: 'center' }}>Comparativo de Algoritmos</h4>
      <div style={{ height: 250 }}>
        <ResponsiveContainer>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis dataKey="name" stroke="#aaa" fontSize={10} tickFormatter={(v) => v.split(' ')[0]} />
            <YAxis unit="%" domain={[0, 100]} stroke="#aaa" />
            <Tooltip contentStyle={{ backgroundColor: '#333' }} />
            <ReferenceLine y={50} stroke="#666" strokeDasharray="3 3" />
            <Bar dataKey="confidence" name="Certeza">
              {data.map((entry, index) => (
                <Cell key={`cell-md-${index}`} fill={MODEL_COLORS[entry.key] || '#888'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {winnerModel && (
        <p style={{ textAlign: 'center', fontSize: '0.8rem', color: '#888', marginTop: '10px' }}>
          Vencedor: <strong style={{ color: '#fff' }}>{winnerModel.toUpperCase().replace('_', ' ')}</strong>
        </p>
      )}
    </div>
  );
};