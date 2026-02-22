import { type CSSProperties } from 'react';
import { type ToastStyleConfig } from '../types';

export const getToastStyles = (isVisible: boolean, config: ToastStyleConfig): Record<string, CSSProperties> => ({
  overlay: {
    position: 'fixed',
    top: '24px',
    right: '24px',
    zIndex: 9999,
    pointerEvents: isVisible ? 'auto' : 'none',
  },
  glassCard: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '16px',
    minWidth: '340px',
    maxWidth: '400px',
    padding: '20px',
    borderRadius: '12px',
    backgroundColor: 'rgba(22, 28, 36, 0.85)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    boxShadow: '0 20px 40px -4px rgba(0, 0, 0, 0.4)',
    transform: isVisible ? 'translateY(0) scale(1)' : 'translateY(-20px) scale(0.95)',
    opacity: isVisible ? 1 : 0,
    transition: 'all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1)',
  },
  iconBox: {
    background: config.iconBg,
    color: config.iconColor,
    minWidth: '40px',
    height: '40px',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: `0 0 15px ${config.iconBg}`,
  },
  content: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    paddingTop: '2px'
  },
  title: {
    margin: '0 0 6px 0',
    fontSize: '15px',
    fontWeight: '600',
    color: '#FFFFFF',
    letterSpacing: '0.02em'
  },
  message: {
    margin: 0,
    fontSize: '14px',
    color: '#919EAB',
    lineHeight: '1.5',
    fontWeight: '400'
  },
  closeBtn: {
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    padding: '4px',
    marginTop: '-4px',
    marginRight: '-4px',
    borderRadius: '50%',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }
});