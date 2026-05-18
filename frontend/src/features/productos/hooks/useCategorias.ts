/**
 * useCategorias — Hook TanStack Query para listado de categorías.
 */

import { useQuery } from '@tanstack/react-query';
import { getCategorias } from '../services/categoriasApi';
import type { Categoria } from '../services/categoriasApi';

export function useCategorias() {
  return useQuery<Categoria[], Error>({
    queryKey: ['categorias'],
    queryFn: getCategorias,
    staleTime: 1000 * 60 * 10, // 10 minutos — las categorías cambian poco
  });
}
