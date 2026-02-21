import React from "react";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import { ACCENT_COLOR, COLORS, DARK_BG } from "../../utils/constants";
import { formatDateBR } from "../../utils/formatters";

export const StatsCharts = ({ charts, kpis }: { charts: any; kpis: any }) => {
  const diagnosisData = [
    { name: "Arboviroses", value: kpis.arbovirus_count },
    { name: "Glaucoma", value: kpis.glaucoma_count },
  ];

  const learningCurveData = charts.learning_curve.map((item: any) => ({
    ...item,
    dateLabel: formatDateBR(item.date),
  }));

  const cardStyle = {
    background: DARK_BG,
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
  };

  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "20px" }}>
        {/* Gráfico de Evolução */}
        <div style={cardStyle}>
          <h4 style={{ marginBottom: "20px", borderBottom: "1px solid #333", paddingBottom: "10px" }}>
            📈 Evolução da Inteligência Artificial
          </h4>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={learningCurveData}>
                <defs>
                  <linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={ACCENT_COLOR} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={ACCENT_COLOR} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="dateLabel" stroke="#666" style={{ fontSize: "0.8rem" }} />
                <YAxis domain={[50, 100]} stroke="#666" unit="%" style={{ fontSize: "0.8rem" }} />
                <Tooltip contentStyle={{ background: "#252525", border: "1px solid #444", borderRadius: "5px" }} />
                <Area type="monotone" dataKey="accuracy" name="Acurácia" stroke={ACCENT_COLOR} fillOpacity={1} fill="url(#colorAcc)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de Performance */}
        <div style={cardStyle}>
          <h4 style={{ marginBottom: "20px", borderBottom: "1px solid #333", paddingBottom: "10px" }}>
            ⚔️ Performance Média por Algoritmo
          </h4>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.model_performance} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis type="number" domain={[0, 100]} stroke="#666" unit="%" />
                <YAxis type="category" dataKey="name" width={100} stroke="#aaa" fontSize={12} tick={{ fill: "#eee" }} />
                <Tooltip contentStyle={{ background: "#252525", border: "1px solid #444", borderRadius: "5px" }} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
                <Bar dataKey="accuracy" name="Acurácia Média" barSize={25} radius={[0, 4, 4, 0]}>
                  {charts.model_performance.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Gráfico de Patologias */}
      <div style={{ marginTop: "20px", display: "flex", gap: "20px", flexWrap: "wrap" }}>
        <div style={{ flex: 1, ...cardStyle, minWidth: "300px" }}>
          <h4 style={{ textAlign: "center", marginBottom: "20px" }}>Distribuição de Patologias</h4>
          <div style={{ height: 250, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={diagnosisData} cx="50%" cy="50%" innerRadius={70} outerRadius={90} paddingAngle={5} dataKey="value" stroke="none">
                  <Cell fill="#3498db" />
                  <Cell fill="#e91e63" />
                </Pie>
                <Tooltip contentStyle={{ background: "#252525", border: "1px solid #444" }} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </>
  );
};