/**
 * useCategorias — TanStack Query hooks para gestión de categorías en admin.
 *
 * Hooks:
 * - useCategoriasQuery()     → GET /api/v1/categorias (lista)
 * - useCreateCategoria()     → POST /api/v1/categorias
 * - useUpdateCategoria()     → PUT /api/v1/categorias/{id}
 * - useDeleteCategoria()     → DELETE /api/v1/categorias/{id}
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/shared/context/AuthContext';
import {
  getCategorias,
  createCategoria,
  updateCategoria,
  deleteCategoria,
  type CategoriaCreatePayload,
  type CategoriaUpdatePayload,
} from '../services/adminCategoriasApi';

// ── Query keys ─────────────────────────────────────────────────────────────────

export const categoriasKeys = {
  all: ['admin', 'categorias'] as const,
  list: () => ['admin', 'categorias', 'list'] as const,
};

// ── Hooks ──────────────────────────────────────────────────────────────────────

/**
 * useCategoriasQuery — obtiene la lista completa de categorías.
 */
export function useCategoriasQuery() {
  const { token } = useAuth();
  return useQuery({
    queryKey: categoriasKeys.list(),
    queryFn: () => getCategorias(token!),
    enabled: !!token,
    staleTime: 30_000,
  });
}

/**
 * useCreateCategoria — mutación para crear una categoría.
 * Invalida la query de lista tras el éxito.
 */
export function useCreateCategoria() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CategoriaCreatePayload) => createCategoria(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: categoriasKeys.list() });
    },
  });
}

/**
 * useUpdateCategoria — mutación para actualizar una categoría.
 * Invalida la query de lista tras el éxito.
 */
export function useUpdateCategoria() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaUpdatePayload }) =>
      updateCategoria(token!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: categoriasKeys.list() });
    },
  });
}

/**
 * useDeleteCategoria — mutación para eliminar (soft delete) una categoría.
 * Invalida la query de lista tras el éxito.
 */
export function useDeleteCategoria() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteCategoria(token!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: categoriasKeys.list() });
    },
  });
}
