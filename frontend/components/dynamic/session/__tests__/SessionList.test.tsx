/**
 * SessionList component tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SessionList } from '../SessionList';
import { useSessionStore } from '@/stores';

// Mock the store
jest.mock('@/stores', () => ({
  useSessionStore: jest.fn(),
}));

describe('SessionList', () => {
  const mockSessions = [
    { id: 'session-1', title: 'Session 1', userId: 'user-1', createdAt: Date.now(), updatedAt: Date.now(), messageCount: 5 },
    { id: 'session-2', title: 'Session 2', userId: 'user-1', createdAt: Date.now(), updatedAt: Date.now(), messageCount: 3 },
  ];

  beforeEach(() => {
    (useSessionStore as jest.Mock).mockReturnValue({
      sessions: mockSessions,
      currentSession: mockSessions[0],
      searchQuery: '',
      loadSessions: jest.fn(),
      switchSession: jest.fn(),
    });
  });

  it('renders session list', () => {
    render(<SessionList userId="user-1" />);
    expect(screen.getByText('Session 1')).toBeInTheDocument();
    expect(screen.getByText('Session 2')).toBeInTheDocument();
  });

  it('displays new session button', () => {
    render(<SessionList userId="user-1" />);
    const newButton = screen.getByRole('button', { name: /new/i });
    expect(newButton).toBeInTheDocument();
  });

  it('loads sessions on mount', () => {
    const mockLoadSessions = jest.fn();
    (useSessionStore as jest.Mock).mockReturnValue({
      sessions: mockSessions,
      currentSession: mockSessions[0],
      searchQuery: '',
      loadSessions: mockLoadSessions,
      switchSession: jest.fn(),
    });

    render(<SessionList userId="user-1" />);
    expect(mockLoadSessions).toHaveBeenCalledWith('user-1');
  });

  it('shows empty state when no sessions', () => {
    (useSessionStore as jest.Mock).mockReturnValue({
      sessions: [],
      currentSession: null,
      searchQuery: '',
      loadSessions: jest.fn(),
      switchSession: jest.fn(),
    });

    render(<SessionList userId="user-1" />);
    expect(screen.getByText('No sessions yet')).toBeInTheDocument();
  });

  it('filters sessions by search query', () => {
    (useSessionStore as jest.Mock).mockReturnValue({
      sessions: mockSessions,
      currentSession: mockSessions[0],
      searchQuery: 'Session 1',
      loadSessions: jest.fn(),
      switchSession: jest.fn(),
    });

    render(<SessionList userId="user-1" />);
    expect(screen.getByText('Session 1')).toBeInTheDocument();
    expect(screen.queryByText('Session 2')).not.toBeInTheDocument();
  });
});
