export interface HistoryItem {
  id: number;
  type: "Arbovirose" | "Glaucoma";
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