/**
 * usePedidos — TanStack Query hooks para pedidos.
 *
 * Hooks:
 * - useGestionPedidos(filtros)   → listado de gestión (PEDIDOS/ADMIN)
 * - usePedidoDetalle(id)         → detalle completo de un pedido
 * - useMisPedidos(skip, limit)   → pedidos del cliente autenticado
 * - useUpdateEstado()            → mutación para avanzar estado (FSM)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  listGestion,
  getDetalle,
  listPedidos,
  updateEstado,
  type ListGestionFilters,
} from '../services/pedidoClient';

// ── Query keys ────────────────────────────────────────────────────────────────

export const pedidoKeys = {
  all: ['pedidos'] as const,
  gestion: (filtros: ListGestionFilters) => ['pedidos', 'gestion', filtros] as const,
  detalle: (id: number) => ['pedidos', 'detalle', id] as const,
  misPedidos: (skip: number, limit: number) => ['pedidos', 'mis', skip, limit] as const,
};

// ── Hooks ─────────────────────────────────────────────────────────────────────

/**
 * useGestionPedidos — listado de gestión para PEDIDOS/ADMIN.
 */
export function useGestionPedidos(filtros: ListGestionFilters = {}) {
  return useQuery({
    queryKey: pedidoKeys.gestion(filtros),
    queryFn: () => listGestion(filtros),
    staleTime: 30_000, // 30 segundos
  });
}

/**
 * usePedidoDetalle — detalle completo de un pedido.
 */
export function usePedidoDetalle(id: number | null) {
  return useQuery({
    queryKey: pedidoKeys.detalle(id ?? 0),
    queryFn: () => getDetalle(id!),
    enabled: id !== null && id > 0,
    staleTime: 15_000,
  });
}

/**
 * useMisPedidos — pedidos del cliente autenticado.
 */
export function useMisPedidos(skip: number = 0, limit: number = 10) {
  return useQuery({
    queryKey: pedidoKeys.misPedidos(skip, limit),
    queryFn: () => listPedidos(skip, limit),
    staleTime: 30_000,
  });
}

/**
 * useUpdateEstado — mutación para avanzar estado de un pedido (FSM manual).
 *
 * Al éxito invalida el listado de gestión y el detalle del pedido afectado.
 */
export function useUpdateEstado() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      pedidoId,
      nuevoEstado,
      motivo,
    }: {
      pedidoId: number;
      nuevoEstado: string;
      motivo?: string;
    }) => updateEstado(pedidoId, nuevoEstado, motivo),

    onSuccess: (_data, variables) => {
      // Invalidar detalle del pedido afectado
      queryClient.invalidateQueries({ queryKey: pedidoKeys.detalle(variables.pedidoId) });
      // Invalidar todos los listados de gestión
      queryClient.invalidateQueries({ queryKey: ['pedidos', 'gestion'] });
      // Invalidar mis pedidos (el cliente puede ver el suyo actualizado)
      queryClient.invalidateQueries({ queryKey: ['pedidos', 'mis'] });
    },
  });
}
