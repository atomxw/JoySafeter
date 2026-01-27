/**
 * RetryButton component
 * Button for retrying failed operations
 */

import React from 'react';

interface RetryButtonProps {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export const RetryButton: React.FC<RetryButtonProps> = ({
  onClick,
  disabled = false,
  loading = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="retry-button"
      title="Retry the operation"
    >
      {loading ? '⏳ Retrying...' : '🔄 Retry'}
    </button>
  );
};

RetryButton.displayName = 'RetryButton';
