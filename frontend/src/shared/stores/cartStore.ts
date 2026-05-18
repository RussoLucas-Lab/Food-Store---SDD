/**
 * CartStore — Estado del carrito de compras.
 *
 * Implementado como módulo singleton con persistencia en localStorage.
 * Compatible con el patrón del proyecto (React Context + hooks).
 *
 * REGLA: Nunca acceder al store sin selector.
 * Siempre usar `useCartStore(s => s.items)` — nunca `useCartStore()`.
 *
 * localStorage key: "food-store:cart"
 * Persiste: solo `items` (no acciones/funciones)
 */

const CART_STORAGE_KEY = 'food-store:cart';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface CartItem {
  producto_id: number;
  producto_nombre: string;
  precio: number;
  cantidad: number;
  personalizacion: {
    excluidos: number[]; // IDs de ingredientes excluidos
  };
}

export interface CartCreateDTO {
  items: Array<{
    producto_id: number;
    cantidad: number;
    personalizacion: { excluidos: number[] };
  }>;
  direccion_id: number;
}

export interface CartStore {
  // Estado
  items: CartItem[];

  // Mutaciones
  addItem(
    producto: { id: number; nombre: string; precio: number },
    cantidad: number,
    excluidos?: number[]
  ): void;
  updateQuantity(producto_id: number, cantidad: number): void;
  removeItem(producto_id: number): void;
  clearCart(): void;

  // Getters
  getTotal(): number;
  getCartDTO(direccion_id: number): CartCreateDTO;
}

// ── Suscriptores (patrón observer) ────────────────────────────────────────────

type Listener = () => void;
const listeners: Set<Listener> = new Set();

function notify(): void {
  listeners.forEach((l) => l());
}

// ── Estado interno ────────────────────────────────────────────────────────────

let _items: CartItem[] = [];

// Cargar desde localStorage al iniciar
try {
  const stored = localStorage.getItem(CART_STORAGE_KEY);
  if (stored) {
    _items = JSON.parse(stored) as CartItem[];
  }
} catch {
  _items = [];
}

function persist(): void {
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(_items));
  } catch {
    // localStorage no disponible (SSR, private browsing)
  }
}

// ── Implementación del store ──────────────────────────────────────────────────

function addItem(
  producto: { id: number; nombre: string; precio: number },
  cantidad: number,
  excluidos: number[] = []
): void {
  const existing = _items.find((i) => i.producto_id === producto.id);
  if (existing) {
    // Si ya existe el producto_id, incrementar cantidad
    existing.cantidad += cantidad;
  } else {
    _items = [
      ..._items,
      {
        producto_id: producto.id,
        producto_nombre: producto.nombre,
        precio: producto.precio,
        cantidad,
        personalizacion: { excluidos },
      },
    ];
  }
  persist();
  notify();
}

function updateQuantity(producto_id: number, cantidad: number): void {
  if (cantidad <= 0) {
    // Si cantidad <= 0, quitar el item
    removeItem(producto_id);
    return;
  }
  _items = _items.map((i) =>
    i.producto_id === producto_id ? { ...i, cantidad } : i
  );
  persist();
  notify();
}

function removeItem(producto_id: number): void {
  _items = _items.filter((i) => i.producto_id !== producto_id);
  persist();
  notify();
}

function clearCart(): void {
  _items = [];
  persist();
  notify();
}

function getTotal(): number {
  return _items.reduce((sum, item) => sum + item.precio * item.cantidad, 0);
}

function getCartDTO(direccion_id: number): CartCreateDTO {
  return {
    items: _items.map((i) => ({
      producto_id: i.producto_id,
      cantidad: i.cantidad,
      personalizacion: { excluidos: i.personalizacion.excluidos },
    })),
    direccion_id,
  };
}

// ── Snapshot del store (para hooks) ──────────────────────────────────────────

export function getSnapshot(): CartStore {
  return {
    items: _items,
    addItem,
    updateQuantity,
    removeItem,
    clearCart,
    getTotal,
    getCartDTO,
  };
}

// ── Hook React ────────────────────────────────────────────────────────────────

import { useSyncExternalStore } from 'react';

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/**
 * Hook para acceder al CartStore con selector obligatorio.
 *
 * REGLA: Siempre usar con selector para evitar re-renders innecesarios.
 *
 * @example
 * // Correcto:
 * const items = useCartStore(s => s.items);
 * const addItem = useCartStore(s => s.addItem);
 *
 * // Incorrecto (evitar):
 * const store = useCartStore();  // NO — sin selector
 */
export function useCartStore<T>(selector: (store: CartStore) => T): T {
  return useSyncExternalStore(subscribe, () => selector(getSnapshot()));
}

export default useCartStore;
