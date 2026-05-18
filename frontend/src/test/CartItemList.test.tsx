/**
 * Tests para CartItemList.
 *
 * Verifica que renderiza ítems del store y que los botones
 * invocan las acciones correctas.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import CartItemList from '@/features/pedidos/components/CartItemList';
import { getSnapshot } from '@/shared/stores/cartStore';

// Mock del cartStore para controlar el estado en tests
vi.mock('@/shared/stores/cartStore', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/shared/stores/cartStore')>();
  return actual; // Usar implementación real
});

const mockProducto = { id: 1, nombre: 'Pizza Margherita', precio: 150.0 };
const mockProducto2 = { id: 2, nombre: 'Empanada', precio: 50.0 };

describe('CartItemList', () => {
  beforeEach(() => {
    getSnapshot().clearCart();
  });

  it('13.2.1: renderiza los ítems del store', () => {
    getSnapshot().addItem(mockProducto, 2);
    getSnapshot().addItem(mockProducto2, 1);

    render(<CartItemList />);

    expect(screen.getByText('Pizza Margherita')).toBeInTheDocument();
    expect(screen.getByText('Empanada')).toBeInTheDocument();
  });

  it('muestra mensaje cuando el carrito está vacío', () => {
    render(<CartItemList />);

    expect(screen.getByText(/no hay ítems/i)).toBeInTheDocument();
  });

  it('13.2.2: botón + llama updateQuantity con cantidad+1', () => {
    getSnapshot().addItem(mockProducto, 2);
    render(<CartItemList />);

    const increaseBtn = screen.getByLabelText(/aumentar cantidad de pizza/i);
    fireEvent.click(increaseBtn);

    // La cantidad debe haberse incrementado a 3
    const items = getSnapshot().items;
    expect(items[0].cantidad).toBe(3);
  });

  it('botón - llama updateQuantity con cantidad-1', () => {
    getSnapshot().addItem(mockProducto, 3);
    render(<CartItemList />);

    const decreaseBtn = screen.getByLabelText(/disminuir cantidad de pizza/i);
    fireEvent.click(decreaseBtn);

    const items = getSnapshot().items;
    expect(items[0].cantidad).toBe(2);
  });

  it('13.2.3: botón Quitar llama removeItem', () => {
    getSnapshot().addItem(mockProducto, 2);
    render(<CartItemList />);

    const removeBtn = screen.getByLabelText(/quitar pizza/i);
    fireEvent.click(removeBtn);

    expect(getSnapshot().items).toHaveLength(0);
  });

  it('muestra ingredientes excluidos cuando existen', () => {
    getSnapshot().addItem(mockProducto, 1, [5, 7]);
    render(<CartItemList />);

    expect(screen.getByText(/sin ingredientes: 5, 7/i)).toBeInTheDocument();
  });
});
