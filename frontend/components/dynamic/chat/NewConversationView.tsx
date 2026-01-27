/**
 * NewConversationView component
 * Shows welcome screen when no session is selected
 * User can create or select sessions from the left sidebar
 */

import React from 'react';

interface NewConversationViewProps {
  userId: string;
}

export const NewConversationView: React.FC<NewConversationViewProps> = () => {
  return (
    <div className="chat-main">
      <div className="chat-body">
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Welcome to Chat</h2>
            <p className="text-gray-600">
              Create a new session or select an existing one from the left sidebar to start chatting.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

NewConversationView.displayName = 'NewConversationView';
