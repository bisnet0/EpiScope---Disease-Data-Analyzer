import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import { type GlaucomaApiResponse, type ChartDataPoint } from "../types";
import { formatResponseHtml } from "../utils/formatters";

interface Props {
  result: GlaucomaApiResponse;
  chartData: ChartDataPoint[];
}

export const GlaucomaResultChart: React.FC<Props> = ({ result, chartData }) => (
  <div className="result-box">
    <h3>👁️ Resultado da Visão Computacional</h3>
    <div dangerouslySetInnerHTML={{ __html: formatResponseHtml(result.friendly_response) }} />

    <div style={{ height: 250, marginTop: '20px' }}>
      <ResponsiveContainer>
        <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis type="number" unit="%" domain={[0, 100]} stroke="#aaa" />
          <YAxis type="category" dataKey="name" width={100} stroke="#aaa" />
          <Tooltip contentStyle={{ backgroundColor: '#333' }} />
          <Legend />
          <Bar dataKey="probability" name="Confiança (%)">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  </div>
);