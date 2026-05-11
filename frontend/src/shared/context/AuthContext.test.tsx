import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderWithProviders, screen } from '@/test/utils';
import { useAuth } from '@/shared/context/AuthContext';
import React from 'react';

// Test component that uses AuthContext
const TestComponent: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  return (
    <div>
      <div>{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</div>
      {user && <div>{user.nombre}</div>}
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('provides default auth state', () => {
    renderWithProviders(<TestComponent />);
    expect(screen.getByText('Not authenticated')).toBeInTheDocument();
  });

  it('renders logout button', () => {
    renderWithProviders(<TestComponent />);
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });
});
