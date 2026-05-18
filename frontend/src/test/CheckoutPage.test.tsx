/**
 * Tests para CheckoutPage.
 *
 * Verifica comportamiento del page completo:
 * - Muestra mensaje de carrito vacío si no hay ítems
 * - Renderiza CartItemList y CartSummary si hay ítems
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import CheckoutPage from '@/features/pedidos/pages/CheckoutPage';
import { getSnapshot } from '@/shared/stores/cartStore';

// Mock de DirectionSelector para evitar fetch en tests
vi.mock('@/features/pedidos/components/DirectionSelector', () => ({
  default: ({ onSelect }: { onSelect: (id: number) => void }) => {
    onSelect(1); // Pre-seleccionar dirección 1
    return <div data-testid="direction-selector-mock">DirectionSelector</div>;
  },
}));

const mockProducto = { id: 1, nombre: 'Pizza Margherita', precio: 150.0 };

// Renderizar con MemoryRouter porque CheckoutPage usa <Link>
function renderCheckout() {
  return render(
    <MemoryRouter>
      <CheckoutPage />
    </MemoryRouter>
  );
}

describe('CheckoutPage', () => {
  beforeEach(() => {
    getSnapshot().clearCart();
    vi.clearAllMocks();
  });

  it('13.4.1: muestra mensaje "carrito vacío" si no hay ítems', () => {
    renderCheckout();

    expect(screen.getByTestId('empty-cart')).toBeInTheDocument();
    expect(screen.getByText(/tu carrito está vacío/i)).toBeInTheDocument();
    expect(screen.getByText(/ir al catálogo/i)).toBeInTheDocument();
  });

  it('13.4.2: renderiza CartItemList si hay ítems', () => {
    getSnapshot().addItem(mockProducto, 2);
    renderCheckout();

    expect(screen.getByTestId('cart-item-list')).toBeInTheDocument();
  });

  it('13.4.2: renderiza CartSummary si hay ítems', () => {
    getSnapshot().addItem(mockProducto, 2);
    renderCheckout();

    expect(screen.getByTestId('cart-summary')).toBeInTheDocument();
  });

  it('muestra el título Checkout cuando hay ítems', () => {
    getSnapshot().addItem(mockProducto, 1);
    renderCheckout();

    expect(screen.getByRole('heading', { name: /checkout/i })).toBeInTheDocument();
  });

  it('muestra link "Seguir comprando" cuando hay ítems', () => {
    getSnapshot().addItem(mockProducto, 1);
    renderCheckout();

    expect(screen.getByText(/seguir comprando/i)).toBeInTheDocument();
  });
});
