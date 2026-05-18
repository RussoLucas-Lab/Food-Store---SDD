/**
 * Tests para AdminNav.
 *
 * Verifica que la navegación muestre los enlaces correctos según el rol.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AdminNav from '@/features/admin/components/AdminNav';

// Mock del contexto de autenticación
vi.mock('@/shared/context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from '@/shared/context/AuthContext';

function renderNav() {
  return render(
    <MemoryRouter>
      <AdminNav />
    </MemoryRouter>
  );
}

describe('AdminNav', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rol ADMIN', () => {
    it('muestra todos los enlaces para ADMIN', () => {
      (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
        user: { id: '1', email: 'admin@test.com', nombre: 'Admin', role: 'ADMIN' },
        token: 'token',
        isAuthenticated: true,
        isLoading: false,
      });

      renderNav();

      expect(screen.getByText('Dashboard')).toBeDefined();
      expect(screen.getByText('Usuarios')).toBeDefined();
      expect(screen.getByText('Catálogo')).toBeDefined();
      expect(screen.getByText('Stock')).toBeDefined();
      expect(screen.getByText('Despacho')).toBeDefined();
    });
  });

  describe('Rol STOCK', () => {
    it('muestra solo Catálogo y Stock para STOCK', () => {
      (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
        user: { id: '2', email: 'stock@test.com', nombre: 'Stock', role: 'STOCK' },
        token: 'token',
        isAuthenticated: true,
        isLoading: false,
      });

      renderNav();

      expect(screen.queryByText('Dashboard')).toBeNull();
      expect(screen.queryByText('Usuarios')).toBeNull();
      expect(screen.getByText('Catálogo')).toBeDefined();
      expect(screen.getByText('Stock')).toBeDefined();
      expect(screen.queryByText('Despacho')).toBeNull();
    });
  });

  describe('Rol PEDIDOS', () => {
    it('muestra solo Despacho para PEDIDOS', () => {
      (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
        user: { id: '3', email: 'pedidos@test.com', nombre: 'Pedidos', role: 'PEDIDOS' },
        token: 'token',
        isAuthenticated: true,
        isLoading: false,
      });

      renderNav();

      expect(screen.queryByText('Dashboard')).toBeNull();
      expect(screen.queryByText('Usuarios')).toBeNull();
      expect(screen.queryByText('Catálogo')).toBeNull();
      expect(screen.queryByText('Stock')).toBeNull();
      expect(screen.getByText('Despacho')).toBeDefined();
    });
  });

  describe('Sin usuario', () => {
    it('no muestra ningún enlace de admin si no hay usuario', () => {
      (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });

      renderNav();

      expect(screen.queryByText('Dashboard')).toBeNull();
      expect(screen.queryByText('Usuarios')).toBeNull();
    });
  });
});
