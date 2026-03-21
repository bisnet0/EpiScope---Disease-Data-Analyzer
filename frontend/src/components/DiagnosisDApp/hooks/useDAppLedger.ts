import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../../context/AuthContext";
import { fetchDiagnosisHistory } from "../services/dapp-service";
import { sendDiagnosisToCartesi } from "../services/blockchain-service";
import { type HistoryItem, type ToastState } from "../types";
import { DAPP_ADDRESS } from "../utils/constants";
import { shortenAddress } from "../utils/formatters";
import api from "../../../middleware/api";

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
      setToast({
        type: "error",
        title: "Carteira Desconectada",
        message: "Por favor, conecte sua MetaMask para assinar o registro.",
      });
      return;
    }

    setSendingId(item.id);

    try {
      setToast({
        type: "info",
        title: "Processando...",
        message: `Enviando Input para Blockchain...`,
      });

      const txHash = await sendDiagnosisToCartesi(item, signer, walletAddress);

      await api.post("/blockchain/register", {
        diagnosis_id: item.id,
        type: item.type,
        tx_hash: txHash,
        payload: item,
      });

      setToast({
        type: "success",
        title: "Registro Concluído!",
        message: `Diagnóstico imutável gerado.\nHash: ${shortenAddress(txHash)}`,
      });

      await loadHistory();
    } catch (error: any) {
      console.error("Erro no fluxo de Registro:", error);

      let displayMessage =
        error.response?.data?.error || error.message || "Falha na transação.";
      if (
        error.code === 4001 ||
        displayMessage.includes("user rejected action")
      ) {
        displayMessage = "Transação cancelada pelo usuário.";
      }
      const maxLength = 120;
      if (displayMessage.length > maxLength) {
        displayMessage = displayMessage.substring(0, maxLength) + "...";
      }

      setToast({
        type: "error",
        title: "Erro ao Registrar",
        message: displayMessage,
      });
    } finally {
      setSendingId(null);
    }
  };

  return {
    state: { history, loading, sendingId, toast },
    auth: { walletAddress, connectWallet, signer },
    actions: { handleRegisterOnChain, closeToast, loadHistory },
  };
};
