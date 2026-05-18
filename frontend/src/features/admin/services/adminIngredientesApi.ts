/**
 * adminIngredientesApi — funciones para consumir los endpoints CRUD de ingredientes.
 *
 * Endpoints:
 * - GET    /api/v1/ingredientes          → listar ingredientes
 * - POST   /api/v1/ingredientes          → crear ingrediente
 * - PUT    /api/v1/ingredientes/{id}     → actualizar ingrediente
 * - DELETE /api/v1/ingredientes/{id}     → eliminar (soft delete) ingrediente
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Types ──────────────────────────────────────────────────────────────────────

export type UnidadMedida = 'gramos' | 'litros' | 'unidades' | 'kilos' | 'mililitros';

export interface Ingrediente {
  id: number;
  nombre: string;
  descripcion: string;
  unidad_medida: string;
  cantidad_stock: number;
  cantidad_minima: number;
  cantidad_reservada: number;
  stock_disponible: number;
  alerta_stock_bajo: boolean;
  categoria_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface IngredienteListResponse {
  ingredientes: Ingrediente[];
  total: number;
  skip: number;
  limit: number;
}

export interface IngredienteCreatePayload {
  nombre: string;
  unidad_medida: UnidadMedida;
  cantidad_stock: number;
  cantidad_minima: number;
  descripcion?: string;
  categoria_id?: number | null;
}

export interface IngredienteUpdatePayload {
  nombre?: string;
  descripcion?: string;
  cantidad_stock?: number;
  cantidad_minima?: number;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

// ── API functions ──────────────────────────────────────────────────────────────

/**
 * Listar todos los ingredientes.
 */
export async function getIngredientes(token: string): Promise<Ingrediente[]> {
  const response = await axios.get<IngredienteListResponse>(
    `${BASE_URL}/api/v1/ingredientes`,
    {
      headers: authHeaders(token),
      params: { limit: 100 },
    }
  );
  return response.data.ingredientes;
}

/**
 * Crear un nuevo ingrediente.
 */
export async function createIngrediente(
  token: string,
  data: IngredienteCreatePayload
): Promise<Ingrediente> {
  const response = await axios.post<Ingrediente>(
    `${BASE_URL}/api/v1/ingredientes`,
    data,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Actualizar un ingrediente existente.
 * Solo permite editar nombre, descripcion, cantidad_stock, cantidad_minima.
 */
export async function updateIngrediente(
  token: string,
  id: number,
  data: IngredienteUpdatePayload
): Promise<Ingrediente> {
  const response = await axios.put<Ingrediente>(
    `${BASE_URL}/api/v1/ingredientes/${id}`,
    data,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Eliminar (soft delete) un ingrediente.
 */
export async function deleteIngrediente(token: string, id: number): Promise<void> {
  await axios.delete(`${BASE_URL}/api/v1/ingredientes/${id}`, {
    headers: authHeaders(token),
  });
}
