/**
 * Tests para DashboardPage.
 *
 * Verifica que los estados de carga y error sean independientes por gráfico.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import DashboardPage from '@/features/admin/pages/DashboardPage';

// Mock de los hooks de métricas
vi.mock('@/features/admin/hooks/useMetricas', () => ({
  useMetricasResumen: vi.fn(),
  useMetricasVentas: vi.fn(),
  useMetricasProductosTop: vi.fn(),
  useMetricasPedidosEstado: vi.fn(),
}));

vi.mock('@/shared/context/AuthContext', () => ({
  useAuth: vi.fn().mockReturnValue({
    user: { id: '1', email: 'admin@test.com', role: 'ADMIN' },
    token: 'mock-token',
  }),
}));

// Mock de recharts para evitar errores de canvas
vi.mock('recharts', () => ({
  LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Bar: () => null,
  PieChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Pie: () => null,
  Cell: () => null,
  Legend: () => null,
}));

import {
  useMetricasResumen,
  useMetricasVentas,
  useMetricasProductosTop,
  useMetricasPedidosEstado,
} from '@/features/admin/hooks/useMetricas';

import React from 'react';

function renderDashboard() {
  return render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>
  );
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default: todos cargando
    (useMetricasResumen as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: false,
      isError: false,
    });
    (useMetricasVentas as ReturnType<typeof vi.fn>).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    });
    (useMetricasProductosTop as ReturnType<typeof vi.fn>).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    });
    (useMetricasPedidosEstado as ReturnType<typeof vi.fn>).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    });
  });

  it('renderiza el título del dashboard', () => {
    renderDashboard();
    expect(screen.getByText('Dashboard')).toBeDefined();
  });

  it('muestra estados de carga independientes por KPI card', () => {
    (useMetricasResumen as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: true,
      isError: false,
    });

    renderDashboard();

    // Las KPI cards deben mostrar el estado de carga
    const loadingElements = screen.getAllByLabelText('Cargando...');
    expect(loadingElements.length).toBeGreaterThanOrEqual(1);
  });

  it('muestra KPIs cuando hay datos', () => {
    (useMetricasResumen as ReturnType<typeof vi.fn>).mockReturnValue({
      data: {
        ventas_totales: 1500,
        cantidad_pedidos: 10,
        cantidad_usuarios: 50,
        productos_sin_stock: 2,
      },
      isLoading: false,
      isError: false,
    });

    renderDashboard();

    // Valores de los KPIs deben estar presentes
    expect(screen.getByText(/1.500/i)).toBeDefined();
    // cantidad_pedidos = 10 → appears as KPI value
    const allTens = screen.getAllByText(/^10$/);
    expect(allTens.length).toBeGreaterThanOrEqual(1);
  });

  it('muestra error independiente en KPI card cuando hay error de resumen', () => {
    (useMetricasResumen as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: false,
      isError: true,
    });

    renderDashboard();

    // Debe haber múltiples errores (uno por cada KPI card)
    const errors = screen.getAllByText('Error al cargar');
    expect(errors.length).toBeGreaterThanOrEqual(1);
  });
});
