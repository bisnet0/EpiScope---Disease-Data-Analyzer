import React from "react";
import { ClipboardData, Trophy, Cpu } from "react-bootstrap-icons";
import { DARK_BG } from "../../utils/constants";

const StatCard = ({ title, value, icon, color, sub }: any) => (
  <div
    style={{
      background: DARK_BG,
      padding: "20px",
      borderRadius: "10px",
      borderLeft: `4px solid ${color}`,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      boxShadow: "0 4px 6px rgba(0,0,0,0.2)",
    }}
  >
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "10px" }}>
      <span style={{ color: "#aaa", fontSize: "0.85rem", fontWeight: "bold", textTransform: "uppercase" }}>{title}</span>
      <span style={{ color: color }}>{icon}</span>
    </div>
    <div style={{ fontSize: "1.8rem", fontWeight: "bold", color: "#fff" }}>{value}</div>
    {sub && <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "5px" }}>{sub}</div>}
  </div>
);

export const KPICards = ({ kpis }: { kpis: any }) => {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px", marginBottom: "30px" }}>
      <StatCard title="Diagnósticos (Filtrado)" value={kpis.total_diagnoses} icon={<ClipboardData size={24} />} color="#3498db" />
      <StatCard title="Melhor Acurácia (Neste Filtro)" value={`${kpis.best_ai_accuracy}%`} icon={<Trophy size={24} />} color="#f1c40f" />
      <StatCard title="Treinamentos Realizados" value={kpis.total_trainings} icon={<Cpu size={24} />} color="#9b59b6" />
      <StatCard
        title="Status Blockchain"
        value="Ativo"
        sub="Consenso Local"
        icon={<div style={{ width: 10, height: 10, background: "#2ecc71", borderRadius: "50%" }} />}
        color="#2ecc71"
      />
    </div>
  );
};