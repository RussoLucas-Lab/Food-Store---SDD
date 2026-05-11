import React from 'react';
import { AuthProvider } from './AuthContext';
import { ThemeProvider } from './ThemeContext';
import { NotificationProvider } from './NotificationContext';

/**
 * ContextProviders: Combines all context providers
 * Wrap App with this component to enable all global state
 */
export const ContextProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>
    <ThemeProvider>
      <NotificationProvider>{children}</NotificationProvider>
    </ThemeProvider>
  </AuthProvider>
);

// Export individual providers and hooks
export { AuthProvider, useAuth } from './AuthContext';
export type { User, UserRole, AuthContextType } from './AuthContext';

export { ThemeProvider, useTheme } from './ThemeContext';
export type { Theme, ThemeContextType } from './ThemeContext';

export { NotificationProvider, useNotification } from './NotificationContext';
export type { Notification, NotificationType, NotificationContextType } from './NotificationContext';
