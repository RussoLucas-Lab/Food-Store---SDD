/**
 * adminUsuariosApi — funciones para consumir los endpoints de gestión de usuarios.
 *
 * Endpoints:
 * - GET  /api/v1/admin/usuarios
 * - PATCH /api/v1/admin/usuarios/{id}
 * - PATCH /api/v1/admin/usuarios/{id}/activo
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface UsuarioAdmin {
  id: number;
  email: string;
  nombre: string | null;
  role: string;
  is_active: boolean;
  roles: string[];
}

export interface UsuariosListResponse {
  items: UsuarioAdmin[];
  total: number;
  page: number;
  size: number;
}

export interface UsuariosListParams {
  page?: number;
  size?: number;
  q?: string;
  rol?: string;
  activo?: boolean;
}

export interface UsuarioUpdatePayload {
  nombre?: string;
  email?: string;
  role?: string;
  roles?: string[];
}

export interface UsuarioActivoPayload {
  activo: boolean;
}

// ── API functions ──────────────────────────────────────────────────────────────

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Listar usuarios con paginación, búsqueda y filtros.
 */
export async function listUsuarios(
  token: string,
  params: UsuariosListParams = {}
): Promise<UsuariosListResponse> {
  const response = await axios.get<UsuariosListResponse>(
    `${BASE_URL}/api/v1/admin/usuarios`,
    {
      headers: authHeaders(token),
      params: {
        ...(params.page && { page: params.page }),
        ...(params.size && { size: params.size }),
        ...(params.q && { q: params.q }),
        ...(params.rol && { rol: params.rol }),
        ...(params.activo !== undefined && { activo: params.activo }),
      },
    }
  );
  return response.data;
}

/**
 * Editar datos y/o rol de un usuario.
 */
export async function updateUsuario(
  token: string,
  userId: number,
  payload: UsuarioUpdatePayload
): Promise<UsuarioAdmin> {
  const response = await axios.patch<UsuarioAdmin>(
    `${BASE_URL}/api/v1/admin/usuarios/${userId}`,
    payload,
    { headers: authHeaders(token) }
  );
  return response.data;
}

/**
 * Activar o desactivar la cuenta de un usuario.
 */
export async function toggleUsuarioActivo(
  token: string,
  userId: number,
  activo: boolean
): Promise<UsuarioAdmin> {
  const response = await axios.patch<UsuarioAdmin>(
    `${BASE_URL}/api/v1/admin/usuarios/${userId}/activo`,
    { activo },
    { headers: authHeaders(token) }
  );
  return response.data;
}
