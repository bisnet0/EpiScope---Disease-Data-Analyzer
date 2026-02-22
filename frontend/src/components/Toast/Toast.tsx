import React from 'react';
import { type ToastProps } from './types';
import { TOAST_CONFIG } from './utils/constants';
import { getToastStyles } from './utils/styles';
import { useToastAnimation } from './hooks/useToastAnimation';
import { CloseButton } from './components/CloseButton';

const Toast: React.FC<ToastProps> = ({ title, message, type = 'info', onClose, duration = 4000 }) => {
  const { isVisible, triggerClose } = useToastAnimation(duration, onClose);
  
  const styleConfig = TOAST_CONFIG[type] || TOAST_CONFIG.info;
  const styles = getToastStyles(isVisible, styleConfig);

  return (
    <div style={styles.overlay}>
      <div style={styles.glassCard}>
        
        <div style={styles.iconBox}>
          {styleConfig.icon}
        </div>
        
        <div style={styles.content}>
          {title && <h4 style={styles.title}>{title}</h4>}
          <p style={styles.message}>{message}</p>
        </div>

        <CloseButton onClick={triggerClose} baseStyle={styles.closeBtn} />
        
      </div>
    </div>
  );
};

export default Toast;