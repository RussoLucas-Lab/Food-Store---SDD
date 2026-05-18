/**
 * ProductoGrid — Grilla responsiva de ProductoCard.
 *
 * - 3 columnas en desktop, 2 en tablet, 1 en mobile
 * - Muestra 6 SkeletonCard durante la carga
 * - Empty state si no hay productos
 */

import React from 'react';
import { Link } from 'react-router-dom';
import SkeletonCard from '@/shared/components/atoms/SkeletonCard';
import ProductoCard from './ProductoCard';
import type { ProductoListItem } from '../services/productosApi';

interface ProductoGridProps {
  productos: ProductoListItem[] | undefined;
  isLoading: boolean;
  error?: Error | null;
}

const ProductoGrid: React.FC<ProductoGridProps> = ({ productos, isLoading, error }) => {
  if (error) {
    return (
      <div className="text-center py-16 text-red-600">
        <p className="text-lg font-medium">Error al cargar los productos</p>
        <p className="text-sm text-red-400 mt-1">{error.message}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (!productos || productos.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-gray-400 text-5xl mb-4">🍽️</div>
        <p className="text-xl font-semibold text-gray-700">
          No encontramos productos
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Probá con otros filtros o explorá todo el catálogo.
        </p>
        <Link
          to="/productos"
          className="inline-block mt-4 text-blue-600 hover:underline text-sm"
        >
          Ver todos los productos
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {productos.map((p) => (
        <ProductoCard key={p.id} producto={p} />
      ))}
    </div>
  );
};

export default ProductoGrid;
