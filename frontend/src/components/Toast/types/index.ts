import { type ReactNode } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastProps {
  title?: string;
  message: string;
  type?: ToastType;
  isCloseable?: boolean;
  onClose?: () => void;
  duration?: number;
}

export interface ToastStyleConfig {
  iconBg: string;
  iconColor: string;
  icon: ReactNode;
}

export interface CloseButtonProps {
  onClick: () => void;
}

export interface ToastContextData {
  showToast: (props: Omit<ToastProps, "onClose">) => void;
}
