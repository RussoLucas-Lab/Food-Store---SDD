/**
 * useProducto — Hook TanStack Query para detalle de un producto por ID.
 */

import { useQuery } from '@tanstack/react-query';
import { getProductoById } from '../services/productosApi';
import type { Producto } from '../services/productosApi';

export function useProducto(id: number | null) {
  return useQuery<Producto, Error>({
    queryKey: ['productos', id],
    queryFn: () => getProductoById(id!),
    enabled: id !== null && !isNaN(id),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}
