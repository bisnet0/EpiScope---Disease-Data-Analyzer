export interface HistoryItem {
  id: number | string;

  type: "Arbovirose" | "Glaucoma" | "Saúde da Mulher" | "Raio-X (Tórax)";

  date: string;
  details: string;
  result: any;
  signature?: string;
}

export interface ToastState {
  message: string;
  type: "success" | "error" | "info";
  title?: string;
}

export interface DAppHeaderProps {
  walletAddress: string | null;
  connectWallet: () => void;
}

export interface HistoryTableProps {
  history: HistoryItem[];
  walletAddress: string | null;
  sendingId: number | string | null;
  onRegisterOnChain: (item: HistoryItem) => void;
}
