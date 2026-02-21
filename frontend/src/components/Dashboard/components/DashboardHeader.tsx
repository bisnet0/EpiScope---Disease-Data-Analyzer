import React from "react";
import { Activity, Filter, ArrowRepeat } from "react-bootstrap-icons";
import { ACCENT_COLOR } from "../utils/constants";

const selectStyle: React.CSSProperties = {
  background: "#333",
  color: "#fff",
  border: "1px solid #555",
  padding: "8px 12px",
  borderRadius: "6px",
  cursor: "pointer",
  outline: "none",
  fontSize: "0.9rem",
};

interface HeaderProps {
  periodFilter: string;
  setPeriodFilter: (v: string) => void;
  modelFilter: string;
  setModelFilter: (v: string) => void;
  onRefresh: () => void;
  loading: boolean;
}

export const DashboardHeader: React.FC<HeaderProps> = ({
  periodFilter,
  setPeriodFilter,
  modelFilter,
  setModelFilter,
  onRefresh,
  loading,
}) => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "20px",
        flexWrap: "wrap",
        gap: "15px",
      }}
    >
      <h2 style={{ margin: 0, display: "flex", alignItems: "center", gap: "10px" }}>
        <Activity color={ACCENT_COLOR} /> Analytics em Tempo Real
      </h2>

      <div
        style={{
          display: "flex",
          gap: "10px",
          background: "#252525",
          padding: "10px",
          borderRadius: "8px",
          border: "1px solid #333",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "5px", color: "#aaa", fontSize: "0.9rem", marginRight: "10px" }}>
          <Filter /> Filtros:
        </div>

        <select value={periodFilter} onChange={(e) => setPeriodFilter(e.target.value)} style={selectStyle}>
          <option value="all">📅 Todo o Período</option>
          <option value="24h">🕒 Últimas 24 Horas</option>
          <option value="7d">📅 Últimos 7 Dias</option>
          <option value="30d">📅 Últimos 30 Dias</option>
        </select>

        <select value={modelFilter} onChange={(e) => setModelFilter(e.target.value)} style={selectStyle}>
          <option value="all">🤖 Todos os Modelos</option>
          <option value="xgboost">🚀 XGBoost</option>
          <option value="random_forest">🌲 Random Forest</option>
          <option value="decision_tree">🌳 Decision Tree</option>
          <option value="glaucoma">🚀🌲 Híbrido</option>
        </select>

        <button
          onClick={onRefresh}
          title="Atualizar Agora"
          style={{ background: "transparent", border: "none", color: "#fff", cursor: "pointer", padding: "0 5px" }}
        >
          <ArrowRepeat size={20} className={loading ? "spin" : ""} />
        </button>
      </div>
    </div>
  );
};