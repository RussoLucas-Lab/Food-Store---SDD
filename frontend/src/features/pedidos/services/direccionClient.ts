/**
 * direccionClient — Cliente HTTP para la API de direcciones de entrega.
 *
 * Métodos:
 * - getDirecciones()            → GET    /api/v1/clientes/me/direcciones
 * - createDireccion(dto)        → POST   /api/v1/clientes/me/direcciones
 * - updateDireccion(id, dto)    → PUT    /api/v1/clientes/me/direcciones/{id}
 * - deleteDireccion(id)         → DELETE /api/v1/clientes/me/direcciones/{id}
 * - setDireccionPredeterminada(id) → PUT /api/v1/clientes/me/direcciones/{id}/predeterminada
 *
 * Estado de servidor → TanStack Query hooks (no Zustand).
 */

import { httpClient, handleApiError } from '../../../shared/services/httpClient';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface DireccionEntregaResponse {
  id: number;
  cliente_id: number;
  calle: string;
  numero: string;
  ciudad: string;
  provincia: string;
  codigo_postal: string;
  piso: string | null;
  departamento: string | null;
  referencia: string | null;
  es_predeterminada: boolean;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface DireccionCreateDTO {
  calle: string;
  numero: string;
  ciudad: string;
  provincia: string;
  codigo_postal: string;
  piso?: string | null;
  departamento?: string | null;
  referencia?: string | null;
  es_predeterminada?: boolean;
}

export interface DireccionUpdateDTO {
  calle?: string;
  numero?: string;
  ciudad?: string;
  provincia?: string;
  codigo_postal?: string;
  piso?: string | null;
  departamento?: string | null;
  referencia?: string | null;
  es_predeterminada?: boolean;
}

// ── Base URL ──────────────────────────────────────────────────────────────────

const BASE = '/api/v1/clientes/me/direcciones';

// ── API calls ─────────────────────────────────────────────────────────────────

/**
 * Obtener todas las direcciones activas del cliente autenticado.
 * GET /api/v1/clientes/me/direcciones
 */
export async function getDirecciones(): Promise<DireccionEntregaResponse[]> {
  try {
    const response = await httpClient.get<DireccionEntregaResponse[]>(BASE);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Crear una nueva dirección de entrega.
 * POST /api/v1/clientes/me/direcciones
 */
export async function createDireccion(
  dto: DireccionCreateDTO
): Promise<DireccionEntregaResponse> {
  try {
    const response = await httpClient.post<DireccionEntregaResponse>(BASE, dto);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Actualizar campos de una dirección existente.
 * PUT /api/v1/clientes/me/direcciones/{id}
 */
export async function updateDireccion(
  id: number,
  dto: DireccionUpdateDTO
): Promise<DireccionEntregaResponse> {
  try {
    const response = await httpClient.put<DireccionEntregaResponse>(`${BASE}/${id}`, dto);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Eliminar (soft-delete) una dirección.
 * DELETE /api/v1/clientes/me/direcciones/{id}
 */
export async function deleteDireccion(id: number): Promise<void> {
  try {
    await httpClient.delete(`${BASE}/${id}`);
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Marcar una dirección como predeterminada.
 * PUT /api/v1/clientes/me/direcciones/{id}/predeterminada
 */
export async function setDireccionPredeterminada(
  id: number
): Promise<DireccionEntregaResponse> {
  try {
    const response = await httpClient.put<DireccionEntregaResponse>(
      `${BASE}/${id}/predeterminada`
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

const direccionClient = {
  getDirecciones,
  createDireccion,
  updateDireccion,
  deleteDireccion,
  setDireccionPredeterminada,
};

export default direccionClient;
