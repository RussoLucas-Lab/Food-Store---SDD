/**
 * adminCategoriasApi — funciones para consumir los endpoints CRUD de categorías.
 *
 * Endpoints:
 * - GET    /api/v1/categorias            → listar categorías
 * - POST   /api/v1/categorias            → crear categoría
 * - PUT    /api/v1/categorias/{id}       → actualizar categoría
 * - DELETE /api/v1/categorias/{id}       → eliminar (soft delete) categoría
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoriaListResponse {
  items: Categoria[];
  total: number;
  skip: number;
  limit: number;
}

export interface CategoriaCreatePayload {
  nombre: string;
  descripcion?: string;
}

export interface CategoriaUpdatePayload {
  nombre?: string;
  descripcion?: string;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

// ── API functions ──────────────────────────────────────────────────────────────

/**
 * Listar todas las categorías (incluye inactivas para admin).
 */
export async function getCategorias(token: string): Promise<Categoria[]> {
  const response = await axios.get<CategoriaListResponse>(
    `${BASE_URL}/api/v1/categorias`,
    {
      headers: authHeaders(token),
      params: { limit: 100, include_inactive: true },
    }
  );
  return response.data.items;
}

/**
 * Crear una nueva categoría.
 */
export async function createCategoria(
  token: string,
  data: CategoriaCreatePayload
): Promise<Categoria> {
  const response = await axios.post<Categoria>(
    `${BASE_URL}/api/v1/categorias`,
    data,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Actualizar una categoría existente.
 */
export async function updateCategoria(
  token: string,
  id: number,
  data: CategoriaUpdatePayload
): Promise<Categoria> {
  const response = await axios.put<Categoria>(
    `${BASE_URL}/api/v1/categorias/${id}`,
    data,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Eliminar (soft delete) una categoría.
 */
export async function deleteCategoria(token: string, id: number): Promise<void> {
  await axios.delete(`${BASE_URL}/api/v1/categorias/${id}`, {
    headers: authHeaders(token),
  });
}
