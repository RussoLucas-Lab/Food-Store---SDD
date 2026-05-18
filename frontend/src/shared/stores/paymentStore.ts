/**
 * PaymentStore — Estado efímero del proceso de pago con MercadoPago.
 *
 * NO persiste en localStorage — estado solo válido durante la sesión de pago.
 * Sigue el mismo patrón singleton que cartStore y authStore (useSyncExternalStore).
 *
 * REGLA: Nunca acceder al store sin selector.
 * Siempre usar `usePaymentStore(s => s.status)` — nunca `usePaymentStore()`.
 *
 * Sin persistencia: los datos de pago son efímeros y no deben sobrevivir
 * una recarga de página (el usuario debería reiniciar el flujo de pago).
 */

import { useSyncExternalStore } from 'react';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface PaymentState {
  /** Estado del pago según MercadoPago (approved, pending, rejected, cancelled, null) */
  status: string | null;
  /** ID del pago en MercadoPago (disponible tras confirmación) */
  mpPaymentId: string | null;
  /** ID del pedido asociado al proceso de pago actual */
  pedidoId: string | null;
  /** Mensaje de error si el pago falló */
  error: string | null;

  /** Registrar resultado del pago tras respuesta de MP */
  setPaymentResult: (status: string, mpPaymentId: string) => void;
  /** Asociar un pedido al proceso de pago */
  setPedidoId: (id: string) => void;
  /** Registrar un error en el proceso de pago */
  setError: (error: string) => void;
  /** Limpiar todo el estado (para reiniciar flujo de pago) */
  reset: () => void;
}

// ── Suscriptores (patrón observer) ────────────────────────────────────────────

type Listener = () => void;
const listeners: Set<Listener> = new Set();

function notify(): void {
  listeners.forEach((l) => l());
}

// ── Estado interno (SIN persistencia — efímero) ───────────────────────────────

let _status: string | null = null;
let _mpPaymentId: string | null = null;
let _pedidoId: string | null = null;
let _error: string | null = null;

// ── Implementación del store ──────────────────────────────────────────────────

/**
 * Registrar el resultado del pago.
 * Llamar después de recibir respuesta del backend (POST /api/v1/pagos).
 */
function setPaymentResult(status: string, mpPaymentId: string): void {
  _status = status;
  _mpPaymentId = mpPaymentId;
  _error = null;
  notify();
}

/**
 * Asociar el pedido al flujo de pago actual.
 * Llamar desde CheckoutPage justo antes de redirigir a PaymentPage.
 */
function setPedidoId(id: string): void {
  _pedidoId = id;
  notify();
}

/**
 * Registrar un error en el proceso de pago.
 * Llamar cuando falla el POST /api/v1/pagos.
 */
function setError(error: string): void {
  _error = error;
  _status = null;
  notify();
}

/**
 * Limpiar todo el estado del pago.
 * Llamar al terminar el flujo (éxito o abandono).
 */
function reset(): void {
  _status = null;
  _mpPaymentId = null;
  _pedidoId = null;
  _error = null;
  notify();
}

// ── Snapshot del store (para hooks) ──────────────────────────────────────────

export function getSnapshot(): PaymentState {
  return {
    status: _status,
    mpPaymentId: _mpPaymentId,
    pedidoId: _pedidoId,
    error: _error,
    setPaymentResult,
    setPedidoId,
    setError,
    reset,
  };
}

// ── Hook React ────────────────────────────────────────────────────────────────

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/**
 * Hook para acceder al PaymentStore con selector obligatorio.
 *
 * REGLA: Siempre usar con selector para evitar re-renders innecesarios.
 *
 * @example
 * // Correcto:
 * const status = usePaymentStore(s => s.status);
 * const setPedidoId = usePaymentStore(s => s.setPedidoId);
 *
 * // Incorrecto (evitar):
 * const store = usePaymentStore();  // NO — sin selector
 */
export function usePaymentStore<T>(selector: (store: PaymentState) => T): T {
  return useSyncExternalStore(subscribe, () => selector(getSnapshot()));
}

export default usePaymentStore;
