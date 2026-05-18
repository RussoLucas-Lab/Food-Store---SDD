/**
 * useMetricas — TanStack Query hooks para métricas del admin.
 *
 * Hooks:
 * - useMetricasResumen()       → GET /admin/metricas/resumen
 * - useMetricasVentas(params)  → GET /admin/metricas/ventas
 * - useMetricasProductosTop()  → GET /admin/metricas/productos-top
 * - useMetricasPedidosEstado() → GET /admin/metricas/pedidos-por-estado
 */

import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/shared/context/AuthContext';
import {
  getResumenMetricas,
  getVentas,
  getProductosTop,
  getPedidosPorEstado,
  type VentasQueryParams,
  type ProductosTopQueryParams,
  type PedidosEstadoQueryParams,
} from '../services/adminMetricasApi';

// ── Query keys ─────────────────────────────────────────────────────────────────

export const metricasKeys = {
  all: ['admin', 'metricas'] as const,
  resumen: () => ['admin', 'metricas', 'resumen'] as const,
  ventas: (params: VentasQueryParams) => ['admin', 'metricas', 'ventas', params] as const,
  productosTop: (params: ProductosTopQueryParams) =>
    ['admin', 'metricas', 'productos-top', params] as const,
  pedidosEstado: (params: PedidosEstadoQueryParams) =>
    ['admin', 'metricas', 'pedidos-estado', params] as const,
};

// ── Hooks ──────────────────────────────────────────────────────────────────────

/**
 * useMetricasResumen — KPIs generales del negocio.
 */
export function useMetricasResumen() {
  const { token } = useAuth();
  return useQuery({
    queryKey: metricasKeys.resumen(),
    queryFn: () => getResumenMetricas(token!),
    enabled: !!token,
    staleTime: 60_000, // 1 minuto
  });
}

/**
 * useMetricasVentas — serie temporal de ventas con filtros de fecha y granularidad.
 */
export function useMetricasVentas(params: VentasQueryParams = {}) {
  const { token } = useAuth();
  return useQuery({
    queryKey: metricasKeys.ventas(params),
    queryFn: () => getVentas(token!, params),
    enabled: !!token,
    staleTime: 60_000,
  });
}

/**
 * useMetricasProductosTop — ranking de productos más vendidos.
 */
export function useMetricasProductosTop(params: ProductosTopQueryParams = {}) {
  const { token } = useAuth();
  return useQuery({
    queryKey: metricasKeys.productosTop(params),
    queryFn: () => getProductosTop(token!, params),
    enabled: !!token,
    staleTime: 60_000,
  });
}

/**
 * useMetricasPedidosEstado — distribución de pedidos por estado.
 */
export function useMetricasPedidosEstado(params: PedidosEstadoQueryParams = {}) {
  const { token } = useAuth();
  return useQuery({
    queryKey: metricasKeys.pedidosEstado(params),
    queryFn: () => getPedidosPorEstado(token!, params),
    enabled: !!token,
    staleTime: 60_000,
  });
}
