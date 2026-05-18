/**
 * AuthStore — Estado de autenticación del usuario.
 *
 * Patrón singleton con persistencia en localStorage.
 * Compatible con cartStore (useSyncExternalStore).
 *
 * REGLA: Nunca acceder al store sin selector.
 * Siempre usar `useAuthStore(s => s.accessToken)` — nunca `useAuthStore()`.
 *
 * localStorage key: "auth-store"
 * Persiste: solo `accessToken` (no el user ni refreshToken).
 */

import { useSyncExternalStore } from 'react';
import type { User } from '@/shared/context/AuthContext';

const AUTH_STORAGE_KEY = 'auth-store';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AuthState {
  accessToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  clearAuth: () => void;
}

// ── Suscriptores (patrón observer) ────────────────────────────────────────────

type Listener = () => void;
const listeners: Set<Listener> = new Set();

function notify(): void {
  listeners.forEach((l) => l());
}

// ── Estado interno ────────────────────────────────────────────────────────────

let _accessToken: string | null = null;
let _user: User | null = null;

// Restaurar solo el accessToken desde localStorage
try {
  const stored = localStorage.getItem(AUTH_STORAGE_KEY);
  if (stored) {
    _accessToken = JSON.parse(stored) as string;
  }
} catch {
  _accessToken = null;
}

function persistToken(): void {
  try {
    if (_accessToken) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(_accessToken));
    } else {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  } catch {
    // localStorage no disponible
  }
}

// ── Implementación del store ──────────────────────────────────────────────────

function setAuth(token: string, user: User): void {
  _accessToken = token;
  _user = user;
  persistToken();
  notify();
}

function clearAuth(): void {
  _accessToken = null;
  _user = null;
  persistToken();
  notify();
}

// ── Snapshot del store (para hooks) ──────────────────────────────────────────

export function getSnapshot(): AuthState {
  return {
    accessToken: _accessToken,
    user: _user,
    isAuthenticated: !!_accessToken && !!_user,
    setAuth,
    clearAuth,
  };
}

// ── Hook React ────────────────────────────────────────────────────────────────

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/**
 * Hook para acceder al AuthStore con selector obligatorio.
 *
 * REGLA: Siempre usar con selector para evitar re-renders innecesarios.
 *
 * @example
 * const token = useAuthStore(s => s.accessToken);
 * const setAuth = useAuthStore(s => s.setAuth);
 */
export function useAuthStore<T>(selector: (store: AuthState) => T): T {
  return useSyncExternalStore(subscribe, () => selector(getSnapshot()));
}

export default useAuthStore;
