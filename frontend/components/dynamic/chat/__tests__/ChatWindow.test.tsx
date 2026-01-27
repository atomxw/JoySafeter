/**
 * ChatWindow component tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChatWindow } from '../ChatWindow';
import { useChatStore, useSessionStore } from '@/stores';

jest.mock('@/stores');
jest.mock('../MessageList', () => ({
  MessageList: () => <div>MessageList</div>,
}));
jest.mock('../MessageInput', () => ({
  MessageInput: () => <div>MessageInput</div>,
}));
jest.mock('@/components/export', () => ({
  ExportMenu: () => <div>ExportMenu</div>,
}));

describe('ChatWindow', () => {
  beforeEach(() => {
    (useChatStore as jest.Mock).mockReturnValue({
      messages: [],
      isLoading: false,
      error: null,
    });

    (useSessionStore as jest.Mock).mockReturnValue({
      currentSession: {
        id: 'session-1',
        title: 'Test Session',
        userId: 'user-1',
        createdAt: Date.now(),
        updatedAt: Date.now(),
        messageCount: 0,
      },
    });
  });

  it('renders chat window', () => {
    render(<ChatWindow sessionId="session-1" />);
    expect(screen.getByText('MessageList')).toBeInTheDocument();
    expect(screen.getByText('MessageInput')).toBeInTheDocument();
  });

  it('displays session title in header', () => {
    render(<ChatWindow sessionId="session-1" />);
    expect(screen.getByText('Test Session')).toBeInTheDocument();
  });

  it('displays export menu', () => {
    render(<ChatWindow sessionId="session-1" />);
    expect(screen.getByText('ExportMenu')).toBeInTheDocument();
  });

  it('displays default title when no session', () => {
    (useSessionStore as jest.Mock).mockReturnValue({
      currentSession: null,
    });

    render(<ChatWindow sessionId="session-1" />);
    expect(screen.getByText('New Conversation')).toBeInTheDocument();
  });

  it('renders with messages', () => {
    const mockMessages = [
      {
        id: 'msg-1',
        content: 'Hello',
        role: 'user' as const,
        timestamp: Date.now(),
        sessionId: 'session-1',
      },
    ];

    (useChatStore as jest.Mock).mockReturnValue({
      messages: mockMessages,
      isLoading: false,
      error: null,
    });

    render(<ChatWindow sessionId="session-1" />);
    expect(screen.getByText('MessageList')).toBeInTheDocument();
  });
});
