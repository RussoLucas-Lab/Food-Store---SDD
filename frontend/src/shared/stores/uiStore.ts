/**
 * UiStore — Estado global de UI (no persistido).
 *
 * Implementado como módulo singleton con el mismo patrón que cartStore.
 * No persiste en localStorage.
 *
 * Estado gestionado:
 * - cartOpen: visibilidad del CartDrawer
 * - sidebarOpen: visibilidad del Sidebar
 * - confirmModal: datos del modal de confirmación genérico
 *
 * REGLA: Nunca acceder al store sin selector.
 * Siempre usar `useUiStore(s => s.cartOpen)` — nunca `useUiStore()`.
 */

import { useSyncExternalStore } from 'react';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ConfirmModal {
  open: boolean;
  message: string;
  onConfirm: () => void;
}

export interface UiStore {
  // Estado
  cartOpen: boolean;
  sidebarOpen: boolean;
  confirmModal: ConfirmModal | null;

  // Acciones
  setCartOpen(open: boolean): void;
  setSidebarOpen(open: boolean): void;
  openConfirmModal(message: string, onConfirm: () => void): void;
  closeConfirmModal(): void;
}

// ── Suscriptores (patrón observer) ────────────────────────────────────────────

type Listener = () => void;
const listeners: Set<Listener> = new Set();

function notify(): void {
  listeners.forEach((l) => l());
}

// ── Estado interno ────────────────────────────────────────────────────────────

let _cartOpen = false;
let _sidebarOpen = false;
let _confirmModal: ConfirmModal | null = null;

// ── Implementación del store ──────────────────────────────────────────────────

function setCartOpen(open: boolean): void {
  _cartOpen = open;
  notify();
}

function setSidebarOpen(open: boolean): void {
  _sidebarOpen = open;
  notify();
}

function openConfirmModal(message: string, onConfirm: () => void): void {
  _confirmModal = { open: true, message, onConfirm };
  notify();
}

function closeConfirmModal(): void {
  _confirmModal = null;
  notify();
}

// ── Snapshot del store (para hooks) ──────────────────────────────────────────

export function getUiSnapshot(): UiStore {
  return {
    cartOpen: _cartOpen,
    sidebarOpen: _sidebarOpen,
    confirmModal: _confirmModal,
    setCartOpen,
    setSidebarOpen,
    openConfirmModal,
    closeConfirmModal,
  };
}

// ── Hook React ────────────────────────────────────────────────────────────────

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/**
 * Hook para acceder al UiStore con selector obligatorio.
 *
 * REGLA: Siempre usar con selector para evitar re-renders innecesarios.
 *
 * @example
 * // Correcto:
 * const cartOpen = useUiStore(s => s.cartOpen);
 * const setCartOpen = useUiStore(s => s.setCartOpen);
 *
 * // Incorrecto (evitar):
 * const store = useUiStore();  // NO — sin selector
 */
export function useUiStore<T>(selector: (store: UiStore) => T): T {
  return useSyncExternalStore(subscribe, () => selector(getUiSnapshot()));
}

export default useUiStore;
