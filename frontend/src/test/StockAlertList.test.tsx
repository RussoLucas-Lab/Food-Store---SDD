/**
 * Tests para StockAlertList.
 *
 * Verifica:
 * - Recalcula alertas al cambiar el umbral configurable
 * - Muestra todos los productos bajo el umbral
 * - Muestra mensaje positivo cuando no hay alertas
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StockAlertList from '@/features/admin/components/StockAlertList';
import React from 'react';

const mockProductos = [
  { id: 1, nombre: 'Pizza', stock: 0 },
  { id: 2, nombre: 'Empanada', stock: 3 },
  { id: 3, nombre: 'Milanesa', stock: 10 },
  { id: 4, nombre: 'Hamburguesa', stock: 5 },
];

describe('StockAlertList', () => {
  it('muestra alerta para productos sin stock con umbral default (5)', () => {
    render(<StockAlertList productos={mockProductos} />);

    // Pizza (0) y Empanada (3) deben aparecer como alertas con umbral 5
    expect(screen.getByText('Pizza')).toBeDefined();
    expect(screen.getByText('Empanada')).toBeDefined();
    // Hamburguesa (5) también está en el umbral
    expect(screen.getByText('Hamburguesa')).toBeDefined();
    // Milanesa (10) no debe aparecer
    expect(screen.queryByText('Milanesa')).toBeNull();
  });

  it('recalcula alertas al cambiar el umbral a 2', () => {
    render(<StockAlertList productos={mockProductos} umbral={2} />);

    // Solo Pizza (0) debe aparecer
    expect(screen.getByText('Pizza')).toBeDefined();
    // Empanada (3) no debe aparecer con umbral 2
    expect(screen.queryByText('Empanada')).toBeNull();
    // Milanesa no debe aparecer
    expect(screen.queryByText('Milanesa')).toBeNull();
  });

  it('recalcula alertas al cambiar el umbral a 8', () => {
    render(<StockAlertList productos={mockProductos} umbral={8} />);

    // Pizza (0), Empanada (3), Hamburguesa (5) deben aparecer
    expect(screen.getByText('Pizza')).toBeDefined();
    expect(screen.getByText('Empanada')).toBeDefined();
    expect(screen.getByText('Hamburguesa')).toBeDefined();
    // Milanesa (10) no debe aparecer con umbral 8
    expect(screen.queryByText('Milanesa')).toBeNull();
  });

  it('muestra mensaje positivo cuando todos tienen stock suficiente', () => {
    const productosConStock = [
      { id: 1, nombre: 'Pizza', stock: 20 },
      { id: 2, nombre: 'Empanada', stock: 15 },
    ];

    render(<StockAlertList productos={productosConStock} umbral={5} />);

    expect(
      screen.getByText(/Todos los productos tienen stock suficiente/i)
    ).toBeDefined();
  });

  it('muestra SIN STOCK para productos con stock 0', () => {
    render(<StockAlertList productos={[{ id: 1, nombre: 'Pizza', stock: 0 }]} umbral={5} />);

    expect(screen.getByText('SIN STOCK')).toBeDefined();
  });

  it('muestra la cantidad correcta de unidades para stocks bajos', () => {
    render(
      <StockAlertList
        productos={[{ id: 2, nombre: 'Empanada', stock: 3 }]}
        umbral={5}
      />
    );

    expect(screen.getByText('3 unid.')).toBeDefined();
  });

  it('lista vacía muestra mensaje positivo', () => {
    render(<StockAlertList productos={[]} umbral={5} />);

    expect(
      screen.getByText(/Todos los productos tienen stock suficiente/i)
    ).toBeDefined();
  });
});
