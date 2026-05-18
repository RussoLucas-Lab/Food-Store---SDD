import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getSnapshot } from '@/shared/stores/authStore';
import { loginApi, getMeApi, logoutApi } from '@/features/auth/services/authClient';

export type UserRole = 'ADMIN' | 'USER' | 'GUEST';

export interface User {
  id: string;
  email: string;
  nombre: string;
  role: UserRole;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  hasRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function mapRol(rol: string): UserRole {
  if (rol === 'ADMIN' || rol === 'admin') return 'ADMIN';
  if (rol === 'CLIENT' || rol === 'customer') return 'USER';
  return 'GUEST';
}

/**
 * AuthProvider: manages authentication state and persistence
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize from authStore (which reads from localStorage)
  useEffect(() => {
    const stored = getSnapshot();
    if (!stored.accessToken) {
      setIsLoading(false);
      return;
    }
    setToken(stored.accessToken);
    if (stored.user) {
      setUser(stored.user);
      setIsLoading(false);
    } else {
      // Token en localStorage pero user solo en memoria → re-fetch tras page refresh
      getMeApi(stored.accessToken)
        .then((me) => {
          const mappedUser: User = {
            id: me.id,
            email: me.email,
            nombre: me.nombre,
            role: mapRol(me.role),
          };
          setUser(mappedUser);
          getSnapshot().setAuth(stored.accessToken!, mappedUser);
        })
        .catch(() => {
          getSnapshot().clearAuth();
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokenResponse = await loginApi(email, password);
    const me = await getMeApi(tokenResponse.access_token);
    const mappedUser: User = {
      id: me.id,
      email: me.email,
      nombre: me.nombre,
      role: mapRol(me.role),
    };
    getSnapshot().setAuth(tokenResponse.access_token, mappedUser);
    setToken(tokenResponse.access_token);
    setUser(mappedUser);
  }, []);

  const logout = useCallback(() => {
    if (token) {
      logoutApi(token).catch(() => {
        // Ignore logout API errors — always clear local state
      });
    }
    getSnapshot().clearAuth();
    setUser(null);
    setToken(null);
  }, [token]);

  const isAuthenticated = !!token && !!user;

  const hasRole = useCallback(
    (role: UserRole) => {
      if (!user) return false;
      if (role === 'GUEST') return true;
      return user.role === role || user.role === 'ADMIN';
    },
    [user]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        logout,
        isAuthenticated,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

/**
 * useAuth hook: consume AuthContext
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
