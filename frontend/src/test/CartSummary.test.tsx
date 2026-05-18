/**
 * Tests para CartSummary.
 *
 * Verifica que muestra el total correcto dado el estado del store.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import CartSummary from '@/features/pedidos/components/CartSummary';
import { getSnapshot } from '@/shared/stores/cartStore';

const mockProducto = { id: 1, nombre: 'Pizza', precio: 150.0 };
const mockProducto2 = { id: 2, nombre: 'Empanada', precio: 50.0 };

describe('CartSummary', () => {
  beforeEach(() => {
    getSnapshot().clearCart();
  });

  it('13.3.1: muestra total correcto dado el estado del store', () => {
    getSnapshot().addItem(mockProducto, 2);   // 300
    getSnapshot().addItem(mockProducto2, 3);  // 150
    // Total esperado: 450

    render(<CartSummary />);

    // Tanto subtotal como total muestran $450.00 (sin costo de envío)
    const amounts = screen.getAllByText('$450.00');
    expect(amounts.length).toBeGreaterThanOrEqual(1);
  });

  it('muestra subtotal correcto', () => {
    getSnapshot().addItem(mockProducto, 1); // 150

    render(<CartSummary />);

    // Subtotal y total deben ser iguales (sin costo de envío)
    const amounts = screen.getAllByText('$150.00');
    expect(amounts.length).toBeGreaterThanOrEqual(1);
  });

  it('muestra Gratis para el envío', () => {
    getSnapshot().addItem(mockProducto, 1);
    render(<CartSummary />);

    expect(screen.getByText('Gratis')).toBeInTheDocument();
  });

  it('muestra $0.00 cuando el carrito está vacío', () => {
    render(<CartSummary />);

    // Subtotal y Total ambos muestran $0.00 cuando el carrito está vacío
    const zeroAmounts = screen.getAllByText('$0.00');
    expect(zeroAmounts.length).toBeGreaterThanOrEqual(1);
  });
});
