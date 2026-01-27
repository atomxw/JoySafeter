/**
 * LoadingIndicator component
 * Displays a loading animation
 */

import React from 'react';

interface LoadingIndicatorProps {
  message?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message = 'Loading...',
}) => {
  return (
    <div className="loading-indicator">
      <span></span>
      <span></span>
      <span></span>
      {message && <span className="ml-2">{message}</span>}
    </div>
  );
};

LoadingIndicator.displayName = 'LoadingIndicator';
