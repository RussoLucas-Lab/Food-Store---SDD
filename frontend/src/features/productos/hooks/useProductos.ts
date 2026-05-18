/**
 * useProductos — Hook TanStack Query para listado de productos.
 *
 * Soporta filtro por categoría y búsqueda por nombre.
 */

import { useQuery } from '@tanstack/react-query';
import { getProductos } from '../services/productosApi';
import type { ProductosParams, ProductoListItem } from '../services/productosApi';

export function useProductos(params: ProductosParams = {}) {
  return useQuery<ProductoListItem[], Error>({
    queryKey: ['productos', params],
    queryFn: () => getProductos(params),
    staleTime: 1000 * 60 * 2, // 2 minutos
  });
}
