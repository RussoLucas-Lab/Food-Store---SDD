/**
 * adminMetricasApi — funciones para consumir los endpoints de métricas del admin.
 *
 * Endpoints:
 * - GET /api/v1/admin/metricas/resumen
 * - GET /api/v1/admin/metricas/ventas
 * - GET /api/v1/admin/metricas/productos-top
 * - GET /api/v1/admin/metricas/pedidos-por-estado
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface ResumenMetricas {
  ventas_totales: number;
  cantidad_pedidos: number;
  cantidad_usuarios: number;
  productos_sin_stock: number;
}

export interface PuntoVenta {
  periodo: string;  // ISO date string
  monto: number;
}

export interface ProductoTop {
  producto_id: number;
  nombre: string;
  cantidad_vendida: number;
}

export interface PedidoPorEstado {
  estado: string;
  cantidad: number;
}

export type Granularidad = 'dia' | 'semana' | 'mes';

export interface VentasQueryParams {
  desde?: string;
  hasta?: string;
  granularidad?: Granularidad;
}

export interface ProductosTopQueryParams {
  top?: number;
  desde?: string;
  hasta?: string;
}

export interface PedidosEstadoQueryParams {
  desde?: string;
  hasta?: string;
}

// ── API functions ──────────────────────────────────────────────────────────────

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Obtener KPIs generales del negocio.
 */
export async function getResumenMetricas(token: string): Promise<ResumenMetricas> {
  const response = await axios.get<ResumenMetricas>(
    `${BASE_URL}/api/v1/admin/metricas/resumen`,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Obtener serie temporal de ventas.
 */
export async function getVentas(
  token: string,
  params: VentasQueryParams = {}
): Promise<PuntoVenta[]> {
  const response = await axios.get<PuntoVenta[]>(
    `${BASE_URL}/api/v1/admin/metricas/ventas`,
    {
      headers: authHeaders(token),
      params: {
        ...(params.desde && { desde: params.desde }),
        ...(params.hasta && { hasta: params.hasta }),
        ...(params.granularidad && { granularidad: params.granularidad }),
      },
    }
  );
  return response.data;
}

/**
 * Obtener ranking de productos más vendidos.
 */
export async function getProductosTop(
  token: string,
  params: ProductosTopQueryParams = {}
): Promise<ProductoTop[]> {
  const response = await axios.get<ProductoTop[]>(
    `${BASE_URL}/api/v1/admin/metricas/productos-top`,
    {
      headers: authHeaders(token),
      params: {
        ...(params.top && { top: params.top }),
        ...(params.desde && { desde: params.desde }),
        ...(params.hasta && { hasta: params.hasta }),
      },
    }
  );
  return response.data;
}

/**
 * Obtener distribución de pedidos por estado.
 */
export async function getPedidosPorEstado(
  token: string,
  params: PedidosEstadoQueryParams = {}
): Promise<PedidoPorEstado[]> {
  const response = await axios.get<PedidoPorEstado[]>(
    `${BASE_URL}/api/v1/admin/metricas/pedidos-por-estado`,
    {
      headers: authHeaders(token),
      params: {
        ...(params.desde && { desde: params.desde }),
        ...(params.hasta && { hasta: params.hasta }),
      },
    }
  );
  return response.data;
}
