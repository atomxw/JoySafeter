/**
 * SessionItem component tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SessionItem } from '../SessionItem';

describe('SessionItem', () => {
  const mockSession = {
    id: 'session-1',
    title: 'Test Session',
    userId: 'user-1',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messageCount: 5,
  };

  it('renders session title', () => {
    render(
      <SessionItem
        session={mockSession}
        isActive={false}
        onSelect={jest.fn()}
      />
    );
    expect(screen.getByText('Test Session')).toBeInTheDocument();
  });

  it('shows active state', () => {
    const { container } = render(
      <SessionItem
        session={mockSession}
        isActive={true}
        onSelect={jest.fn()}
      />
    );
    const item = container.querySelector('[class*="active"]');
    expect(item).toBeInTheDocument();
  });

  it('calls onSelect when clicked', async () => {
    const user = userEvent.setup();
    const mockOnSelect = jest.fn();
    render(
      <SessionItem
        session={mockSession}
        isActive={false}
        onSelect={mockOnSelect}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);
    expect(mockOnSelect).toHaveBeenCalled();
  });

  it('displays message count', () => {
    render(
      <SessionItem
        session={mockSession}
        isActive={false}
        onSelect={jest.fn()}
      />
    );
    expect(screen.getByText(/5/)).toBeInTheDocument();
  });
});
