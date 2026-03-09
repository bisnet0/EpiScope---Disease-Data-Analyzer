import { type ToastType, type ToastStyleConfig } from '../types';

export const TOAST_CONFIG: Record<ToastType, ToastStyleConfig> = {
  success: {
    iconBg: 'rgba(34, 197, 94, 0.15)',
    iconColor: '#4ade80',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    )
  },
  error: {
    iconBg: 'rgba(239, 68, 68, 0.15)',
    iconColor: '#f87171',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    )
  },
  info: {
    iconBg: 'rgba(59, 130, 246, 0.15)',
    iconColor: '#60a5fa',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
      </svg>
    )
  }
};