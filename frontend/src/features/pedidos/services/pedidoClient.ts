/**
 * pedidoClient — Cliente HTTP para la API de pedidos.
 *
 * Métodos:
 * - createPedido(dto) → POST /api/v1/pedidos
 * - listPedidos(skip, limit) → GET /api/v1/pedidos
 * - getPedidoDetail(id) → GET /api/v1/pedidos/{id}
 * - getMyDirecciones() → GET /api/v1/clientes/me/direcciones (stub)
 */

import { httpClient, handleApiError } from '../../../shared/services/httpClient';
import type { CartCreateDTO } from '../../../shared/stores/cartStore';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface PedidoResponse {
  id: number;
  cliente_id: number;
  estado: string;
  total: number;
  costo_envio: number;
  creado_en: string;
}

export interface DetallePedidoResponse {
  id: number;
  producto_id: number;
  nombre_snapshot: string;
  cantidad: number;
  precio_snapshot: number;
  personalizacion: number[];
  creado_en: string;
}

export interface HistorialEstadoPedidoResponse {
  id: number;
  estado_anterior: string | null;
  estado_nuevo: string;
  usuario_id: number | null;
  timestamp: string;
  observacion: string | null;
}

export interface PedidoDetailResponse extends PedidoResponse {
  direccion_snapshot: Record<string, string>;
  detalles: DetallePedidoResponse[];
  historial: HistorialEstadoPedidoResponse[];
  actualizado_en: string;
}

export interface DireccionResponse {
  id: number;
  nombre: string;
  direccion: string;
  telefono?: string;
}

// ── Client ────────────────────────────────────────────────────────────────────

const BASE = '/api/v1/pedidos';
const CLIENTES_BASE = '/api/v1/clientes';

/**
 * Crear un nuevo pedido desde el carrito.
 * POST /api/v1/pedidos
 */
export async function createPedido(dto: CartCreateDTO): Promise<PedidoResponse> {
  try {
    const response = await httpClient.post<PedidoResponse>(BASE, dto);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Listar pedidos del cliente autenticado.
 * GET /api/v1/pedidos
 */
export async function listPedidos(
  skip: number = 0,
  limit: number = 10
): Promise<PedidoResponse[]> {
  try {
    const response = await httpClient.get<PedidoResponse[]>(BASE, {
      params: { skip, limit },
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Obtener detalle completo de un pedido.
 * GET /api/v1/pedidos/{id}
 */
export async function getPedidoDetail(id: number): Promise<PedidoDetailResponse> {
  try {
    const response = await httpClient.get<PedidoDetailResponse>(`${BASE}/${id}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Obtener las direcciones del cliente autenticado.
 * GET /api/v1/clientes/me/direcciones
 *
 * Nota: Este endpoint es un stub — el módulo de clientes actual maneja
 * una sola dirección por cliente. En una versión futura se implementará
 * el endpoint dedicado.
 */
export async function getMyDirecciones(): Promise<DireccionResponse[]> {
  try {
    const response = await httpClient.get<DireccionResponse[]>(
      `${CLIENTES_BASE}/me/direcciones`
    );
    return response.data;
  } catch {
    // En la versión actual la dirección viene del perfil del cliente
    return [];
  }
}

// ── Tipos adicionales para despacho-pedidos ───────────────────────────────────

export interface EstadoUpdateDTO {
  nuevo_estado: string;
  motivo?: string;
}

export interface PedidoGestionResponse {
  id: number;
  cliente_id: number;
  estado: string;
  total: number;
  costo_envio: number;
  creado_en: string;
}

export interface ListGestionFilters {
  estado?: string;
  fecha_desde?: string;  // YYYY-MM-DD
  fecha_hasta?: string;  // YYYY-MM-DD
  skip?: number;
  limit?: number;
}

/**
 * Cambiar el estado de un pedido (FSM manual).
 * PATCH /api/v1/pedidos/{id}/estado
 */
export async function updateEstado(
  id: number,
  nuevoEstado: string,
  motivo?: string
): Promise<PedidoResponse> {
  try {
    const response = await httpClient.patch<PedidoResponse>(`${BASE}/${id}/estado`, {
      nuevo_estado: nuevoEstado,
      motivo: motivo ?? null,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Listar pedidos para gestores con filtros opcionales.
 * GET /api/v1/pedidos/gestion
 */
export async function listGestion(
  filtros: ListGestionFilters = {}
): Promise<PedidoGestionResponse[]> {
  try {
    const params: Record<string, string | number> = {};
    if (filtros.estado) params.estado = filtros.estado;
    if (filtros.fecha_desde) params.fecha_desde = filtros.fecha_desde;
    if (filtros.fecha_hasta) params.fecha_hasta = filtros.fecha_hasta;
    if (filtros.skip !== undefined) params.skip = filtros.skip;
    if (filtros.limit !== undefined) params.limit = filtros.limit;

    const response = await httpClient.get<PedidoGestionResponse[]>(`${BASE}/gestion`, {
      params,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Obtener detalle completo de un pedido.
 * GET /api/v1/pedidos/{id}
 */
export async function getDetalle(id: number): Promise<PedidoDetailResponse> {
  return getPedidoDetail(id);
}

const pedidoClient = {
  createPedido,
  listPedidos,
  getPedidoDetail,
  getMyDirecciones,
  updateEstado,
  listGestion,
  getDetalle,
};

export default pedidoClient;
