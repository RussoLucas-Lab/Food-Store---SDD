/**
 * Tests unitarios para paymentStore.
 *
 * Casos cubiertos:
 * - Estado inicial: todos los campos en null
 * - setPaymentResult: actualiza status y mpPaymentId, limpia error
 * - setPedidoId: actualiza pedidoId
 * - setError: actualiza error, limpia status
 * - reset: regresa todo a null
 * - Sin persistencia: los datos no se guardan en localStorage
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { getSnapshot } from '@/shared/stores/paymentStore';

// Helper para acceder al store directamente (sin hook)
function getStore() {
  return getSnapshot();
}

describe('paymentStore', () => {
  beforeEach(() => {
    // Resetear el store antes de cada test
    getStore().reset();
  });

  // ── Estado inicial ─────────────────────────────────────────────────────────

  describe('initial state', () => {
    it('tiene todos los campos en null al iniciar', () => {
      const store = getStore();

      expect(store.status).toBeNull();
      expect(store.mpPaymentId).toBeNull();
      expect(store.pedidoId).toBeNull();
      expect(store.error).toBeNull();
    });
  });

  // ── setPaymentResult ───────────────────────────────────────────────────────

  describe('setPaymentResult', () => {
    it('actualiza status y mpPaymentId correctamente', () => {
      getStore().setPaymentResult('approved', 'mp-payment-12345');
      const store = getStore();

      expect(store.status).toBe('approved');
      expect(store.mpPaymentId).toBe('mp-payment-12345');
    });

    it('limpia el error al registrar resultado exitoso', () => {
      getStore().setError('Error previo');
      getStore().setPaymentResult('approved', 'mp-abc');
      const store = getStore();

      expect(store.error).toBeNull();
    });

    it('actualiza con estado pending', () => {
      getStore().setPaymentResult('pending', 'mp-999');
      const store = getStore();

      expect(store.status).toBe('pending');
      expect(store.mpPaymentId).toBe('mp-999');
    });

    it('actualiza con estado rejected', () => {
      getStore().setPaymentResult('rejected', '');
      const store = getStore();

      expect(store.status).toBe('rejected');
    });
  });

  // ── setPedidoId ────────────────────────────────────────────────────────────

  describe('setPedidoId', () => {
    it('actualiza pedidoId correctamente', () => {
      getStore().setPedidoId('42');
      const store = getStore();

      expect(store.pedidoId).toBe('42');
    });

    it('puede ser reasignado', () => {
      getStore().setPedidoId('1');
      getStore().setPedidoId('2');
      const store = getStore();

      expect(store.pedidoId).toBe('2');
    });
  });

  // ── setError ───────────────────────────────────────────────────────────────

  describe('setError', () => {
    it('actualiza el campo error', () => {
      getStore().setError('Error de pago: tarjeta rechazada');
      const store = getStore();

      expect(store.error).toBe('Error de pago: tarjeta rechazada');
    });

    it('limpia el status al registrar un error', () => {
      getStore().setPaymentResult('pending', 'mp-123');
      getStore().setError('Error inesperado');
      const store = getStore();

      expect(store.status).toBeNull();
      expect(store.error).toBe('Error inesperado');
    });
  });

  // ── reset ──────────────────────────────────────────────────────────────────

  describe('reset', () => {
    it('regresa todos los campos a null', () => {
      getStore().setPaymentResult('approved', 'mp-xyz');
      getStore().setPedidoId('100');
      getStore().setError('Algún error');

      getStore().reset();
      const store = getStore();

      expect(store.status).toBeNull();
      expect(store.mpPaymentId).toBeNull();
      expect(store.pedidoId).toBeNull();
      expect(store.error).toBeNull();
    });

    it('es idempotente (llamar múltiples veces no causa problemas)', () => {
      getStore().reset();
      getStore().reset();
      const store = getStore();

      expect(store.status).toBeNull();
      expect(store.error).toBeNull();
    });
  });

  // ── Sin persistencia ───────────────────────────────────────────────────────

  describe('no persistence', () => {
    it('no guarda datos en localStorage', () => {
      getStore().setPaymentResult('approved', 'mp-test');
      getStore().setPedidoId('55');

      // El store de pago no debe escribir en localStorage
      const lsKeys = Object.keys(localStorage);
      const hasPagoKey = lsKeys.some((k) => k.includes('pago') || k.includes('payment'));
      expect(hasPagoKey).toBe(false);
    });
  });
});
