/**
 * categoriasApi — Llamadas HTTP al endpoint /api/v1/categorias.
 *
 * Endpoint público: no requiere autenticación (RN-RB10).
 */

import { httpClient } from '@/shared/services/httpClient';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string | null;
  padre_id: number | null;
}

// ── API functions ─────────────────────────────────────────────────────────────

/**
 * Obtener listado de categorías.
 */
export async function getCategorias(): Promise<Categoria[]> {
  const response = await httpClient.get<Categoria[] | { items: Categoria[] }>('/api/v1/categorias');
  const data = response.data;
  return Array.isArray(data) ? data : data.items;
}
