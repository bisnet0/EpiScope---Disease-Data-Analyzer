import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../../context/AuthContext"; // Ajuste o caminho
import { fetchDiagnosisHistory } from "../../../middleware/dapp-service";
import { sendDiagnosisToCartesi } from "../../../middleware/blockchain-service";
import { HistoryItem, ToastState } from "../types";
import { DAPP_ADDRESS } from "../utils/constants";
import { shortenAddress } from "../utils/formatters";

export const useDAppLedger = () => {
  const { walletAddress, connectWallet, signer } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [sendingId, setSendingId] = useState<number | null>(null);
  const [toast, setToast] = useState<ToastState | null>(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchDiagnosisHistory();
      setHistory(data);
    } catch (error) {
      console.error("Erro ao buscar histórico:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const closeToast = () => setToast(null);

  const handleRegisterOnChain = async (item: HistoryItem) => {
    if (!signer || !walletAddress) {
      setToast({ type: "error", message: "Por favor, conecte sua carteira primeiro." });
      connectWallet();
      return;
    }

    setSendingId(item.id);

    try {
      setToast({ type: "info", message: `Enviando Input para DApp ${shortenAddress(DAPP_ADDRESS)}` });
      
      const tx = await sendDiagnosisToCartesi(item, signer, walletAddress);
      
      setToast({ 
        type: "success", 
        message: `Transação enviada para Blockchain!\nHash: ${shortenAddress(tx.hash)}` 
      });
      
    } catch (error: any) {
      console.error("Erro Blockchain:", error);
      setToast({ type: "error", message: "Erro ao registrar: " + (error.reason || error.message) });
    } finally {
      setSendingId(null);
    }
  };

  return {
    state: { history, loading, sendingId, toast },
    auth: { walletAddress, connectWallet },
    actions: { handleRegisterOnChain, closeToast }
  };
};