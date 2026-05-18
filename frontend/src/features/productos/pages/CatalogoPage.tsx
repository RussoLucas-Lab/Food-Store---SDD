/**
 * CatalogoPage — Listado de productos con filtros.
 *
 * Ruta: /productos
 * Compone CatalogoFilters + ProductoGrid.
 * Estado de filtros (categoriaId, search) gestionado localmente.
 */

import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useProductos } from '../hooks/useProductos';
import { useAuth } from '@/shared/context/AuthContext';
import CatalogoFilters from '../components/CatalogoFilters';
import ProductoGrid from '../components/ProductoGrid';

const CatalogoPage: React.FC = () => {
  const { user } = useAuth();
  const [categoriaId, setCategoriaId] = useState<number | undefined>(undefined);
  const [search, setSearch] = useState('');

  const { data, isLoading, error } = useProductos({
    categoria_id: categoriaId,
    search: search || undefined,
  });

  const handleCategoryChange = useCallback((id: number | undefined) => {
    setCategoriaId(id);
  }, []);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Catálogo</h1>
          <p className="text-sm text-gray-500">
            Explorá nuestra selección de productos frescos y deliciosos.
          </p>
        </div>
        {user?.role === 'ADMIN' && (
          <Link
            to="/admin/productos"
            className="shrink-0 inline-flex items-center gap-1.5 bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Gestionar catálogo →
          </Link>
        )}
      </div>

      {/* Filtros */}
      <div className="mb-6">
        <CatalogoFilters
          onCategoryChange={handleCategoryChange}
          onSearchChange={handleSearchChange}
        />
      </div>

      {/* Grilla de productos */}
      <ProductoGrid
        productos={data}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
};

export default CatalogoPage;
