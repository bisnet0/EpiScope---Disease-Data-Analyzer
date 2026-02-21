import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export const ProbabilityChart = ({ data }: { data: any[] }) => (
  <div style={{ flex: '1 1 400px', background: '#252525', padding: '15px', borderRadius: '8px' }}>
    <h4 style={{ textAlign: 'center' }}>Probabilidades (Consenso)</h4>
    <div style={{ height: 250 }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis type="number" unit="%" domain={[0, 100]} stroke="#aaa" />
          <YAxis type="category" dataKey="name" width={100} stroke="#aaa" />
          <Tooltip contentStyle={{ backgroundColor: '#333' }} />
          <Bar dataKey="probability" name="Confiança">
            {data.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  </div>
);