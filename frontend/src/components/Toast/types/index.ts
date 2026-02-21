import { ReactNode } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastProps {
  title?: string;
  message: string;
  type?: ToastType;
  onClose: () => void;
  duration?: number;
}

export interface ToastStyleConfig {
  iconBg: string;
  iconColor: string;
  icon: ReactNode;
}