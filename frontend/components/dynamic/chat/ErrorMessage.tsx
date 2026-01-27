/**
 * ErrorMessage component
 * Displays error messages with retry option
 */

import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  onRetry,
  onDismiss,
}) => {
  return (
    <div className="error-message">
      <div className="error-message-content">
        <span className="error-icon">⚠️</span>
        <div className="error-text">
          <p className="error-title">Error</p>
          <p className="error-description">{message}</p>
        </div>
      </div>
      <div className="error-message-actions">
        {onRetry && (
          <button onClick={onRetry} className="error-button retry">
            Retry
          </button>
        )}
        {onDismiss && (
          <button onClick={onDismiss} className="error-button dismiss">
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
};

ErrorMessage.displayName = 'ErrorMessage';
