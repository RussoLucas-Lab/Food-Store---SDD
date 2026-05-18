import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './AuthContext';
import { ThemeProvider } from './ThemeContext';
import { NotificationProvider } from './NotificationContext';

const queryClient = new QueryClient();

/**
 * ContextProviders: Combines all context providers
 * Wrap App with this component to enable all global state
 */
export const ContextProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <ThemeProvider>
        <NotificationProvider>{children}</NotificationProvider>
      </ThemeProvider>
    </AuthProvider>
  </QueryClientProvider>
);

// Export individual providers and hooks
export { AuthProvider, useAuth } from './AuthContext';
export type { User, UserRole, AuthContextType } from './AuthContext';

export { ThemeProvider, useTheme } from './ThemeContext';
export type { Theme, ThemeContextType } from './ThemeContext';

export { NotificationProvider, useNotification } from './NotificationContext';
export type { Notification, NotificationType, NotificationContextType } from './NotificationContext';
