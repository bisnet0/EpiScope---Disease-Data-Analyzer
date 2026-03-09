import React from 'react';
import { IconButton } from '@chakra-ui/react';
import { useToastThemeFx } from '../styles/theme-fx';
import { type CloseButtonProps } from '../types';

export const CloseButton: React.FC<CloseButtonProps> = ({ onClick }) => {
  const themeFx = useToastThemeFx();

  return (
    <IconButton
      aria-label="Close Toast"
      onClick={onClick}
      variant="ghost"
      size="sm"
      isRound
      color={themeFx.closeIconColor}
      _hover={{
        bg: themeFx.closeIconHoverBg,
        color: themeFx.closeIconHoverColor
      }}
      mt="-4px"
      mr="-4px"
      icon={
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      }
    />
  );
};