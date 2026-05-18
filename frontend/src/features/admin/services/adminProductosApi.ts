/**
 * adminProductosApi — funciones para consumir los endpoints CRUD de productos.
 *
 * Endpoints:
 * - GET    /api/v1/productos             → listar productos
 * - GET    /api/v1/productos/{id}        → detalle de producto
 * - POST   /api/v1/productos             → crear producto
 * - PUT    /api/v1/productos/{id}        → actualizar producto
 * - DELETE /api/v1/productos/{id}        → eliminar (soft delete) producto
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface CategoriaInfo {
  id: number;
  nombre: string;
  descripcion?: string;
}

export interface ProductoIngrediente {
  id: number;
  ingredient_id: number;
  quantity_required: number;
  created_at: string;
  updated_at: string;
}

export interface ProductoIngredienteInput {
  ingredient_id: number;
  quantity_required: number;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  base_price: number;
  status: string;
  stock_disponible: number;
  precio: number;
  disponible: boolean;
  stock: number;
  imagen_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductoDetalle {
  id: number;
  nombre: string;
  descripcion: string;
  base_price: number;
  status: string;
  categories: CategoriaInfo[];
  ingredients: ProductoIngrediente[];
  stock_disponible: number;
  created_at: string;
  updated_at: string;
}

export interface ProductoListResponse {
  items: Producto[];
  total: number;
  skip: number;
  limit: number;
}

export interface ProductoCreatePayload {
  nombre: string;
  base_price: number;
  descripcion?: string;
  categories: number[];
  ingredients: ProductoIngredienteInput[];
}

export interface ProductoUpdatePayload {
  nombre?: string;
  base_price?: number;
  descripcion?: string;
  categories?: number[];
  ingredients?: ProductoIngredienteInput[];
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

// ── API functions ──────────────────────────────────────────────────────────────

/**
 * Listar todos los productos.
 */
export async function getProductos(token: string): Promise<Producto[]> {
  const response = await axios.get<ProductoListResponse>(
    `${BASE_URL}/api/v1/productos`,
    {
      headers: authHeaders(token),
      params: { limit: 100 },
    }
  );
  return response.data.items;
}

/**
 * Obtener el detalle completo de un producto (con categorías e ingredientes).
 */
export async function getProductoDetalle(
  token: string,
  id: number
): Promise<ProductoDetalle> {
  const response = await axios.get<ProductoDetalle>(
    `${BASE_URL}/api/v1/productos/${id}`,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Crear un nuevo producto.
 */
export async function createProducto(
  token: string,
  data: ProductoCreatePayload
): Promise<ProductoDetalle> {
  const response = await axios.post<ProductoDetalle>(
    `${BASE_URL}/api/v1/productos`,
    data,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Actualizar un producto existente.
 */
export async function updateProducto(
  token: string,
  id: number,
  data: ProductoUpdatePayload
): Promise<ProductoDetalle> {
  const response = await axios.put<ProductoDetalle>(
    `${BASE_URL}/api/v1/productos/${id}`,
    data,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Eliminar (soft delete) un producto.
 */
export async function deleteProducto(token: string, id: number): Promise<void> {
  await axios.delete(`${BASE_URL}/api/v1/productos/${id}`, {
    headers: authHeaders(token),
  });
}
