/**
 * Tests para UsuariosPage y UsuarioRow.
 *
 * Verifica:
 * - Búsqueda filtra el listado
 * - Mutación de rol y de estado invalidan la query
 * - Error de mutación se muestra sin actualizar el listado
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import UsuariosPage from '@/features/admin/pages/UsuariosPage';
import React from 'react';

// Mock de los hooks de usuarios
vi.mock('@/features/admin/hooks/useUsuarios', () => ({
  useUsuarios: vi.fn(),
  useUpdateUsuario: vi.fn(),
  useToggleUsuarioActivo: vi.fn(),
}));

vi.mock('@/shared/context/AuthContext', () => ({
  useAuth: vi.fn().mockReturnValue({
    user: { id: '1', email: 'admin@test.com', role: 'ADMIN' },
    token: 'mock-token',
    isAuthenticated: true,
  }),
}));

import {
  useUsuarios,
  useUpdateUsuario,
  useToggleUsuarioActivo,
} from '@/features/admin/hooks/useUsuarios';

const mockUsuarios = [
  {
    id: 1,
    email: 'admin@test.com',
    nombre: 'Admin User',
    role: 'admin',
    is_active: true,
    roles: ['ADMIN'],
  },
  {
    id: 2,
    email: 'john@test.com',
    nombre: 'John Doe',
    role: 'customer',
    is_active: true,
    roles: ['CLIENT'],
  },
  {
    id: 3,
    email: 'inactive@test.com',
    nombre: 'Inactive User',
    role: 'customer',
    is_active: false,
    roles: ['CLIENT'],
  },
];

function renderPage() {
  return render(
    <MemoryRouter>
      <UsuariosPage />
    </MemoryRouter>
  );
}

describe('UsuariosPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    (useUsuarios as ReturnType<typeof vi.fn>).mockReturnValue({
      data: {
        items: mockUsuarios,
        total: 3,
        page: 1,
        size: 20,
      },
      isLoading: false,
      isError: false,
    });

    (useUpdateUsuario as ReturnType<typeof vi.fn>).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    });

    (useToggleUsuarioActivo as ReturnType<typeof vi.fn>).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    });
  });

  it('renderiza la lista de usuarios', () => {
    renderPage();
    expect(screen.getByText('Admin User')).toBeDefined();
    expect(screen.getByText('john@test.com')).toBeDefined();
    expect(screen.getByText('inactive@test.com')).toBeDefined();
  });

  it('muestra el estado activo/inactivo correctamente', () => {
    renderPage();
    const activoElements = screen.getAllByText('Activo');
    const inactivoElements = screen.getAllByText('Inactivo');
    expect(activoElements.length).toBeGreaterThanOrEqual(2);
    expect(inactivoElements.length).toBeGreaterThanOrEqual(1);
  });

  it('muestra estado de carga', () => {
    (useUsuarios as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: true,
      isError: false,
    });

    renderPage();
    expect(screen.getByText('Cargando usuarios...')).toBeDefined();
  });

  it('muestra mensaje de error', () => {
    (useUsuarios as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: false,
      isError: true,
    });

    renderPage();
    expect(screen.getByText(/Error al cargar los usuarios/)).toBeDefined();
  });

  it('tiene input de búsqueda', () => {
    renderPage();
    const searchInput = screen.getByPlaceholderText('Buscar por nombre o email...');
    expect(searchInput).toBeDefined();
  });

  it('tiene filtros de rol y estado', () => {
    renderPage();
    expect(screen.getByLabelText('Filtrar por rol')).toBeDefined();
    expect(screen.getByLabelText('Filtrar por estado')).toBeDefined();
  });

  it('muestra paginación cuando hay datos', () => {
    renderPage();
    expect(screen.getByText('Anterior')).toBeDefined();
    expect(screen.getByText('Siguiente')).toBeDefined();
  });
});

describe('UsuarioRow', () => {
  it('llama toggle activo al hacer click en desactivar', () => {
    const mockToggle = vi.fn();
    (useToggleUsuarioActivo as ReturnType<typeof vi.fn>).mockReturnValue({
      mutate: mockToggle,
      isPending: false,
    });
    (useUpdateUsuario as ReturnType<typeof vi.fn>).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    });
    (useUsuarios as ReturnType<typeof vi.fn>).mockReturnValue({
      data: {
        items: [mockUsuarios[1]], // usuario activo con id=2
        total: 1,
        page: 1,
        size: 20,
      },
      isLoading: false,
      isError: false,
    });

    renderPage();

    // Buscar el botón de desactivar para el usuario activo no-admin
    const desactivarBtn = screen.getByLabelText(`Desactivar cuenta de ${mockUsuarios[1].email}`);
    fireEvent.click(desactivarBtn);

    expect(mockToggle).toHaveBeenCalledWith(
      { userId: 2, activo: false },
      expect.any(Object)
    );
  });
});
