/**
 * productosApi — Llamadas HTTP al endpoint /api/v1/productos.
 *
 * Endpoints públicos: no requieren autenticación para lectura (RN-CA08).
 */

import { httpClient } from '@/shared/services/httpClient';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Ingrediente {
  id: number;
  nombre: string;
  es_alergeno: boolean;
  es_removible: boolean;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio: number;
  stock: number;
  disponible: boolean;
  imagen_url: string | null;
  categorias: Array<{ id: number; nombre: string }>;
  ingredientes: Ingrediente[];
}

export interface ProductoListItem {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio: number;
  stock: number;
  disponible: boolean;
  imagen_url: string | null;
}

export interface ProductosParams {
  categoria_id?: number;
  search?: string;
  page?: number;
  size?: number;
}

export interface ProductosResponse {
  items: ProductoListItem[];
  total: number;
  page: number;
  size: number;
}

// ── API functions ─────────────────────────────────────────────────────────────

/**
 * Obtener listado de productos con filtros y paginación.
 */
export async function getProductos(
  params: ProductosParams = {}
): Promise<ProductoListItem[]> {
  const { page = 1, size = 20, categoria_id, search } = params;

  const queryParams: Record<string, string | number> = {
    skip: (page - 1) * size,
    limit: size,
  };

  if (categoria_id !== undefined) {
    queryParams.categoria_id = categoria_id;
  }
  if (search && search.trim() !== '') {
    queryParams.search = search.trim();
  }

  const response = await httpClient.get<ProductoListItem[] | ProductosResponse>(
    '/api/v1/productos',
    { params: queryParams }
  );

  // El endpoint puede devolver array directo o { items, total, ... }
  const data = response.data;
  if (Array.isArray(data)) {
    return data;
  }
  return data.items;
}

/**
 * Obtener detalle de un producto por ID.
 */
export async function getProductoById(id: number): Promise<Producto> {
  const response = await httpClient.get<Producto>(`/api/v1/productos/${id}`);
  return response.data;
}
