/**
 * useUsuarios — TanStack Query hooks para gestión de usuarios del admin.
 *
 * Hooks:
 * - useUsuarios(params)          → GET /admin/usuarios
 * - useUpdateUsuario()           → PATCH /admin/usuarios/{id}
 * - useToggleUsuarioActivo()     → PATCH /admin/usuarios/{id}/activo
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/shared/context/AuthContext';
import {
  listUsuarios,
  updateUsuario,
  toggleUsuarioActivo,
  type UsuariosListParams,
  type UsuarioUpdatePayload,
} from '../services/adminUsuariosApi';

// ── Query keys ─────────────────────────────────────────────────────────────────

export const usuariosKeys = {
  all: ['admin', 'usuarios'] as const,
  list: (params: UsuariosListParams) => ['admin', 'usuarios', 'list', params] as const,
};

// ── Hooks ──────────────────────────────────────────────────────────────────────

/**
 * useUsuarios — listado de usuarios con paginación, búsqueda y filtros.
 */
export function useUsuarios(params: UsuariosListParams = {}) {
  const { token } = useAuth();
  return useQuery({
    queryKey: usuariosKeys.list(params),
    queryFn: () => listUsuarios(token!, params),
    enabled: !!token,
    staleTime: 30_000, // 30 segundos
  });
}

/**
 * useUpdateUsuario — mutación para editar datos y/o rol de un usuario.
 *
 * Al éxito invalida la query de listado de usuarios.
 */
export function useUpdateUsuario() {
  const queryClient = useQueryClient();
  const { token } = useAuth();

  return useMutation({
    mutationFn: ({
      userId,
      payload,
    }: {
      userId: number;
      payload: UsuarioUpdatePayload;
    }) => updateUsuario(token!, userId, payload),

    onSuccess: () => {
      // Invalidar todos los listados de usuarios para refrescar la UI
      queryClient.invalidateQueries({ queryKey: usuariosKeys.all });
    },
  });
}

/**
 * useToggleUsuarioActivo — mutación para activar/desactivar cuenta de usuario.
 *
 * Al éxito invalida la query de listado de usuarios.
 */
export function useToggleUsuarioActivo() {
  const queryClient = useQueryClient();
  const { token } = useAuth();

  return useMutation({
    mutationFn: ({
      userId,
      activo,
    }: {
      userId: number;
      activo: boolean;
    }) => toggleUsuarioActivo(token!, userId, activo),

    onSuccess: () => {
      // Invalidar todos los listados para refrescar la UI
      queryClient.invalidateQueries({ queryKey: usuariosKeys.all });
    },
  });
}
