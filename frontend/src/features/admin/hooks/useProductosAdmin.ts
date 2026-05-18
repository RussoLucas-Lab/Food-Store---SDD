/**
 * useProductosAdmin — TanStack Query hooks para gestión de productos en admin.
 *
 * Hooks:
 * - useProductosAdminQuery()   → GET /api/v1/productos (lista)
 * - useProductoDetalle(id)     → GET /api/v1/productos/{id} (detalle)
 * - useCreateProducto()        → POST /api/v1/productos
 * - useUpdateProducto()        → PUT /api/v1/productos/{id}
 * - useDeleteProducto()        → DELETE /api/v1/productos/{id}
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/shared/context/AuthContext';
import {
  getProductos,
  getProductoDetalle,
  createProducto,
  updateProducto,
  deleteProducto,
  type ProductoCreatePayload,
  type ProductoUpdatePayload,
} from '../services/adminProductosApi';

// ── Query keys ─────────────────────────────────────────────────────────────────

export const productosAdminKeys = {
  all: ['admin', 'productos'] as const,
  list: () => ['admin', 'productos', 'list'] as const,
  detail: (id: number) => ['admin', 'productos', 'detail', id] as const,
};

// ── Hooks ──────────────────────────────────────────────────────────────────────

/**
 * useProductosAdminQuery — obtiene la lista de productos.
 */
export function useProductosAdminQuery() {
  const { token } = useAuth();
  return useQuery({
    queryKey: productosAdminKeys.list(),
    queryFn: () => getProductos(token!),
    enabled: !!token,
    staleTime: 30_000,
  });
}

/**
 * useProductoDetalle — obtiene el detalle completo de un producto por ID.
 * Incluye categorías e ingredientes asignados.
 */
export function useProductoDetalle(id: number | null) {
  const { token } = useAuth();
  return useQuery({
    queryKey: productosAdminKeys.detail(id!),
    queryFn: () => getProductoDetalle(token!, id!),
    enabled: !!token && id !== null,
    staleTime: 30_000,
  });
}

/**
 * useCreateProducto — mutación para crear un producto.
 * Invalida la query de lista tras el éxito.
 */
export function useCreateProducto() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProductoCreatePayload) => createProducto(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productosAdminKeys.list() });
    },
  });
}

/**
 * useUpdateProducto — mutación para actualizar un producto.
 * Invalida la query de lista y el detalle tras el éxito.
 */
export function useUpdateProducto() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoUpdatePayload }) =>
      updateProducto(token!, id, data),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: productosAdminKeys.list() });
      queryClient.invalidateQueries({ queryKey: productosAdminKeys.detail(id) });
    },
  });
}

/**
 * useDeleteProducto — mutación para eliminar (soft delete) un producto.
 * Invalida la query de lista tras el éxito.
 */
export function useDeleteProducto() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteProducto(token!, id),
    onSuccess: (_data, id) => {
      queryClient.setQueryData(
        productosAdminKeys.list(),
        (old: import('../services/adminProductosApi').Producto[] | undefined) =>
          old ? old.filter((p) => p.id !== id) : []
      );
      queryClient.invalidateQueries({ queryKey: productosAdminKeys.list() });
    },
  });
}
