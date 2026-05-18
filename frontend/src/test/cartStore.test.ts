/**
 * Tests unitarios para cartStore.
 *
 * Prueba todas las operaciones del store: addItem, updateQuantity,
 * removeItem, clearCart, getTotal, getCartDTO.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { getSnapshot } from '@/shared/stores/cartStore';

// Helper para acceder al store directamente (sin hook)
function getStore() {
  return getSnapshot();
}

const mockProducto = {
  id: 1,
  nombre: 'Pizza Margherita',
  precio: 150.0,
};

const mockProducto2 = {
  id: 2,
  nombre: 'Empanada',
  precio: 50.0,
};

describe('cartStore', () => {
  beforeEach(() => {
    // Limpiar el carrito antes de cada test
    getStore().clearCart();
  });

  // ── addItem ─────────────────────────────────────────────────────────────────

  describe('addItem', () => {
    it('13.1.1: agrega un ítem nuevo al carrito', () => {
      getStore().addItem(mockProducto, 2);
      const items = getStore().items;

      expect(items).toHaveLength(1);
      expect(items[0].producto_id).toBe(1);
      expect(items[0].cantidad).toBe(2);
      expect(items[0].producto_nombre).toBe('Pizza Margherita');
    });

    it('13.1.2: addItem con mismo producto_id incrementa la cantidad', () => {
      getStore().addItem(mockProducto, 2);
      getStore().addItem(mockProducto, 3);
      const items = getStore().items;

      expect(items).toHaveLength(1);
      expect(items[0].cantidad).toBe(5); // 2 + 3
    });

    it('agrega excluidos correctamente', () => {
      getStore().addItem(mockProducto, 1, [5, 7]);
      const items = getStore().items;

      expect(items[0].personalizacion.excluidos).toEqual([5, 7]);
    });

    it('agrega múltiples productos distintos', () => {
      getStore().addItem(mockProducto, 1);
      getStore().addItem(mockProducto2, 2);
      const items = getStore().items;

      expect(items).toHaveLength(2);
    });
  });

  // ── updateQuantity ──────────────────────────────────────────────────────────

  describe('updateQuantity', () => {
    it('13.1.3: updateQuantity con 0 elimina el ítem', () => {
      getStore().addItem(mockProducto, 2);
      getStore().updateQuantity(1, 0);
      const items = getStore().items;

      expect(items).toHaveLength(0);
    });

    it('actualiza la cantidad del ítem correctamente', () => {
      getStore().addItem(mockProducto, 2);
      getStore().updateQuantity(1, 5);
      const items = getStore().items;

      expect(items[0].cantidad).toBe(5);
    });

    it('cantidad negativa también elimina el ítem', () => {
      getStore().addItem(mockProducto, 2);
      getStore().updateQuantity(1, -1);
      const items = getStore().items;

      expect(items).toHaveLength(0);
    });
  });

  // ── removeItem ──────────────────────────────────────────────────────────────

  describe('removeItem', () => {
    it('13.1.4: removeItem elimina el ítem correctamente', () => {
      getStore().addItem(mockProducto, 2);
      getStore().addItem(mockProducto2, 1);
      getStore().removeItem(1);
      const items = getStore().items;

      expect(items).toHaveLength(1);
      expect(items[0].producto_id).toBe(2);
    });

    it('no falla si el ítem no existe', () => {
      getStore().addItem(mockProducto, 1);
      expect(() => getStore().removeItem(999)).not.toThrow();
    });
  });

  // ── getTotal ────────────────────────────────────────────────────────────────

  describe('getTotal', () => {
    it('13.1.5: getTotal retorna la suma correcta', () => {
      getStore().addItem(mockProducto, 2);   // 2 × 150 = 300
      getStore().addItem(mockProducto2, 3);  // 3 × 50  = 150

      const total = getStore().getTotal();

      expect(total).toBe(450);
    });

    it('getTotal retorna 0 con carrito vacío', () => {
      expect(getStore().getTotal()).toBe(0);
    });
  });

  // ── clearCart ───────────────────────────────────────────────────────────────

  describe('clearCart', () => {
    it('13.1.6: clearCart vacía el array de ítems', () => {
      getStore().addItem(mockProducto, 2);
      getStore().addItem(mockProducto2, 1);
      getStore().clearCart();

      expect(getStore().items).toHaveLength(0);
    });
  });

  // ── getCartDTO ──────────────────────────────────────────────────────────────

  describe('getCartDTO', () => {
    it('serializa el carrito para el POST /api/v1/pedidos', () => {
      getStore().addItem(mockProducto, 2, [5]);
      const dto = getStore().getCartDTO(10);

      expect(dto.direccion_id).toBe(10);
      expect(dto.items).toHaveLength(1);
      expect(dto.items[0].producto_id).toBe(1);
      expect(dto.items[0].cantidad).toBe(2);
      expect(dto.items[0].personalizacion.excluidos).toEqual([5]);
    });
  });
});
