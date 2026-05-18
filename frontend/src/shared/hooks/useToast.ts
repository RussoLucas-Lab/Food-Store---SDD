/**
 * useToast — Hook para notificaciones toast.
 *
 * Sistema simple sin librería externa. Gestiona una lista de toasts activos
 * con auto-remove después de 3000ms.
 *
 * @example
 * const { toasts, showToast } = useToast();
 * showToast('Producto agregado', 'success');
 */

import { useState, useCallback, useRef } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

let _toastCounter = 0;

export interface UseToastReturn {
  toasts: Toast[];
  showToast: (message: string, type?: ToastType) => void;
  removeToast: (id: string) => void;
}

export function useToast(): UseToastReturn {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timersRef.current.get(id);
    if (timer !== undefined) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
  }, []);

  const showToast = useCallback(
    (message: string, type: ToastType = 'info') => {
      const id = `toast-${++_toastCounter}-${Date.now()}`;
      const newToast: Toast = { id, message, type };
      setToasts((prev) => [...prev, newToast]);

      const timer = setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
        timersRef.current.delete(id);
      }, 3000);

      timersRef.current.set(id, timer);
    },
    []
  );

  return { toasts, showToast, removeToast };
}

// ── Singleton global para acceso desde fuera de React ─────────────────────────
// Permite llamar showToast desde servicios / stores sin prop drilling.

type GlobalToastFn = (message: string, type?: ToastType) => void;
let _globalShowToast: GlobalToastFn | null = null;

export function registerGlobalToast(fn: GlobalToastFn): void {
  _globalShowToast = fn;
}

export function toast(message: string, type: ToastType = 'info'): void {
  if (_globalShowToast) {
    _globalShowToast(message, type);
  } else {
    // Fallback silencioso si no hay provider registrado
    console.warn('[useToast] No global toast registered. Call registerGlobalToast() first.');
  }
}
