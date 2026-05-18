/**
 * useIngredientes — TanStack Query hooks para gestión de ingredientes en admin.
 *
 * Hooks:
 * - useIngredientesQuery()     → GET /api/v1/ingredientes (lista)
 * - useCreateIngrediente()     → POST /api/v1/ingredientes
 * - useUpdateIngrediente()     → PUT /api/v1/ingredientes/{id}
 * - useDeleteIngrediente()     → DELETE /api/v1/ingredientes/{id}
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/shared/context/AuthContext';
import {
  getIngredientes,
  createIngrediente,
  updateIngrediente,
  deleteIngrediente,
  type IngredienteCreatePayload,
  type IngredienteUpdatePayload,
} from '../services/adminIngredientesApi';

// ── Query keys ─────────────────────────────────────────────────────────────────

export const ingredientesKeys = {
  all: ['admin', 'ingredientes'] as const,
  list: () => ['admin', 'ingredientes', 'list'] as const,
};

// ── Hooks ──────────────────────────────────────────────────────────────────────

/**
 * useIngredientesQuery — obtiene la lista completa de ingredientes.
 */
export function useIngredientesQuery() {
  const { token } = useAuth();
  return useQuery({
    queryKey: ingredientesKeys.list(),
    queryFn: () => getIngredientes(token!),
    enabled: !!token,
    staleTime: 30_000,
  });
}

/**
 * useCreateIngrediente — mutación para crear un ingrediente.
 * Invalida la query de lista tras el éxito.
 */
export function useCreateIngrediente() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: IngredienteCreatePayload) => createIngrediente(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ingredientesKeys.list() });
    },
  });
}

/**
 * useUpdateIngrediente — mutación para actualizar un ingrediente.
 * Invalida la query de lista tras el éxito.
 */
export function useUpdateIngrediente() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteUpdatePayload }) =>
      updateIngrediente(token!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ingredientesKeys.list() });
    },
  });
}

/**
 * useDeleteIngrediente — mutación para eliminar (soft delete) un ingrediente.
 * Invalida la query de lista tras el éxito.
 */
export function useDeleteIngrediente() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteIngrediente(token!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ingredientesKeys.list() });
    },
  });
}
