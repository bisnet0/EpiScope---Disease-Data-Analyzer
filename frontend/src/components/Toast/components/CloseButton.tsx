import React, { useState } from 'react';
import { CSSProperties } from 'react';

interface Props {
  onClick: () => void;
  baseStyle: CSSProperties;
}

export const CloseButton: React.FC<Props> = ({ onClick, baseStyle }) => {
  const [isHovered, setIsHovered] = useState(false);

  const hoverStyle: CSSProperties = {
    color: isHovered ? '#fff' : '#637381',
    background: isHovered ? 'rgba(255,255,255,0.1)' : 'transparent',
  };

  return (
    <button
      onClick={onClick}
      style={{ ...baseStyle, ...hoverStyle }}
      aria-label="Close"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  );
};