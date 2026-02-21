import React from "react";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { DARK_BG } from "../../utils/constants";

export const GAAnalysisCharts = ({ gaData }: { gaData: any }) => {
  if (!gaData || !gaData.mutation || gaData.mutation.length === 0) return null;

  const cardStyle = { background: DARK_BG, padding: "20px", borderRadius: "10px" };
  const titleStyle = { fontSize: "0.9rem", color: "#aaa", marginBottom: "15px" };

  return (
    <div style={{ marginTop: "40px", borderTop: "1px solid #333", paddingTop: "20px" }}>
      <h3 style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
        🧬 Teoria Evolutiva: Análise de Hiperparâmetros
      </h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "20px" }}>
        
        {/* Mutação */}
        <div style={cardStyle}>
          <h4 style={titleStyle}>⚡ Taxa de Mutação vs Acurácia</h4>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={gaData.mutation}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="x" type="number" domain={[0, "dataMax"]} stroke="#666" tickFormatter={(v) => `${v * 100}%`} />
                <YAxis domain={["auto", "auto"]} stroke="#666" hide />
                <Tooltip contentStyle={{ background: "#252525" }} formatter={(val: number) => `${val}%`} labelFormatter={(l) => `Mutação: ${l * 100}%`} />
                <Line type="monotone" dataKey="y" stroke="#FF8042" dot={{ r: 3 }} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* População */}
        <div style={cardStyle}>
          <h4 style={titleStyle}>👥 Tamanho da População</h4>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={gaData.population}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="x" stroke="#666" />
                <YAxis domain={[0, 100]} stroke="#666" hide />
                <Tooltip contentStyle={{ background: "#252525" }} cursor={{ fill: "transparent" }} />
                <Bar dataKey="y" fill="#00C49F" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Crossover */}
        <div style={cardStyle}>
          <h4 style={titleStyle}>🧬 Taxa de Crossover</h4>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={gaData.crossover}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="x" stroke="#666" tickFormatter={(v) => `${v * 100}%`} />
                <YAxis domain={["auto", "auto"]} stroke="#666" hide />
                <Tooltip contentStyle={{ background: "#252525" }} labelFormatter={(l) => `Crossover: ${l * 100}%`} />
                <Area type="monotone" dataKey="y" stroke="#8884d8" fill="#8884d8" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
};