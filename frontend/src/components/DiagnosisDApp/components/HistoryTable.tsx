import React from "react";
import { ClockHistory, CheckCircle, CloudUpload } from "react-bootstrap-icons";
import { type HistoryItem } from "../types";
import { formatTimeBR } from "../utils/formatters";

interface Props {
  history: HistoryItem[];
  walletAddress: string | null;
  sendingId: number | null;
  onRegisterOnChain: (item: HistoryItem) => void;
}

export const HistoryTable: React.FC<Props> = ({ history, walletAddress, sendingId, onRegisterOnChain }) => {
  if (history.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px", background: "#1e1e1e", borderRadius: "8px" }}>
        <p>Nenhum diagnóstico encontrado.</p>
        <small style={{ color: "#666" }}>Realize um diagnóstico nas outras abas primeiro.</small>
      </div>
    );
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", color: "#eee", minWidth: "600px" }}>
      <thead>
        <tr style={{ borderBottom: "1px solid #444", textAlign: "left", color: "#888" }}>
          <th style={{ padding: "15px" }}>Data</th>
          <th style={{ padding: "15px" }}>Tipo</th>
          <th style={{ padding: "15px" }}>Resumo</th>
          <th style={{ padding: "15px", textAlign: "right" }}>Ação Blockchain</th>
        </tr>
      </thead>
      <tbody>
        {history.map((item) => (
          <tr key={`${item.type}-${item.id}`} style={{ borderBottom: "1px solid #333", transition: "background 0.2s" }}>
            <td style={{ padding: "15px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <ClockHistory size={14} />
                {new Date(item.date).toLocaleDateString("pt-BR")}
                <small style={{ color: "#666" }}> {formatTimeBR(item.date)}</small>
              </div>
            </td>
            <td style={{ padding: "15px" }}>
              <span style={{
                background: item.type === "Arbovirose" ? "rgba(52, 152, 219, 0.2)" : "rgba(233, 30, 99, 0.2)",
                color: item.type === "Arbovirose" ? "#3498db" : "#e91e63",
                padding: "4px 10px", borderRadius: "12px", fontSize: "0.8rem", fontWeight: "500"
              }}>
                {item.type}
              </span>
            </td>
            <td style={{ padding: "15px", color: "#ccc", fontSize: "0.9rem", maxWidth: "300px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {item.details}
            </td>
            <td style={{ padding: "15px", textAlign: "right" }}>
              {item.signature ? (
                <span title="Registrado na Blockchain" style={{ color: "#2ecc71", display: "flex", alignItems: "center", justifyContent: "flex-end", gap: "5px" }}>
                  <CheckCircle /> Registrado
                </span>
              ) : (
                <button
                  onClick={() => onRegisterOnChain(item)}
                  disabled={sendingId === item.id || !walletAddress}
                  style={{
                    background: "transparent",
                    border: walletAddress ? "1px solid #646cff" : "1px solid #444",
                    color: walletAddress ? "#646cff" : "#666",
                    padding: "6px 12px", fontSize: "0.8rem", borderRadius: "6px",
                    cursor: walletAddress ? "pointer" : "not-allowed",
                    display: "inline-flex", alignItems: "center", gap: "6px", transition: "all 0.2s"
                  }}
                >
                  {sendingId === item.id ? "Assinando..." : <><CloudUpload /> Registrar</>}
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};