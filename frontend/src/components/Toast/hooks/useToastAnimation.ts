import { useState, useEffect, useCallback } from 'react';

export const useToastAnimation = (duration: number, onClose: () => void) => {
  const [isVisible, setIsVisible] = useState(false);

  const triggerClose = useCallback(() => {
    setIsVisible(false);
    setTimeout(onClose, 400); // Tempo da transição de saída
  }, [onClose]);

  useEffect(() => {
    const enterTimer = setTimeout(() => setIsVisible(true), 10);
    const exitTimer = setTimeout(triggerClose, duration);

    return () => {
      clearTimeout(enterTimer);
      clearTimeout(exitTimer);
    };
  }, [duration, triggerClose]);

  return { isVisible, triggerClose };
};