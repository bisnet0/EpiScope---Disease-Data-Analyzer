import React from "react";
import { ShieldCheck } from "react-bootstrap-icons";

interface Props {
  walletAddress: string | null;
  connectWallet: () => void;
}

export const DAppHeader: React.FC<Props> = ({ walletAddress, connectWallet }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "10px" }}>
    <h2 style={{ margin: 0, display: "flex", alignItems: "center" }}>
      <ShieldCheck style={{ marginRight: "10px", color: "#646cff" }} />
      Cartesi DApp Ledger
    </h2>

    {!walletAddress ? (
      <button onClick={connectWallet} className="btn-primary" style={{ background: "#f39c12", padding: "8px 16px" }}>
        🦊 Conectar MetaMask
      </button>
    ) : (
      <div style={{ color: "#2ecc71", border: "1px solid #2ecc71", padding: "5px 15px", borderRadius: "20px", fontSize: "0.9rem" }}>
        🟢 Wallet Conectada
      </div>
    )}
  </div>
);