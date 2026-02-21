import React from "react";
import Toast from "../../components/Toast"; // Importação do componente genérico
import { useDAppLedger } from "./hooks/useDAppLedger";
import { DAppHeader } from "./components/DAppHeader";
import { HistoryTable } from "./components/HistoryTable";

export const DiagnosisDAppForm: React.FC = () => {
  const { state, auth, actions } = useDAppLedger();

  return (
    <div className="container">
      <div className="form-section" style={{ maxWidth: "1000px" }}>
        
        <DAppHeader 
          walletAddress={auth.walletAddress} 
          connectWallet={auth.connectWallet} 
        />

        <p style={{ color: "#aaa", marginBottom: "30px", lineHeight: "1.5" }}>
          Selecione um diagnóstico do seu histórico Web2 para enviar para a camada 
          de execução verificável (Cartesi Machine). Isso cria uma prova 
          criptográfica imutável do resultado.
        </p>

        {state.loading ? (
          <p style={{ textAlign: "center", color: "#666" }}>Carregando histórico...</p>
        ) : (
          <div className="history-list" style={{ overflowX: "auto" }}>
            <HistoryTable
              history={state.history}
              walletAddress={auth.walletAddress}
              sendingId={state.sendingId}
              onRegisterOnChain={actions.handleRegisterOnChain}
            />
          </div>
        )}

      </div>
      
      {state.toast && (
        <Toast 
          type={state.toast.type} 
          message={state.toast.message} 
          onClose={actions.closeToast} 
          title={state.toast.title} 
        />
      )}
    </div>
  );
};