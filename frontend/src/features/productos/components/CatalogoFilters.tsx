/**
 * CatalogoFilters — Filtros del catálogo: categoría + búsqueda por texto.
 *
 * El debounce en el input de texto (300ms) evita queries excesivos.
 */

import React, { useState, useEffect } from 'react';
import { useCategorias } from '../hooks/useCategorias';

interface CatalogoFiltersProps {
  onCategoryChange: (categoriaId: number | undefined) => void;
  onSearchChange: (search: string) => void;
}

const CatalogoFilters: React.FC<CatalogoFiltersProps> = ({
  onCategoryChange,
  onSearchChange,
}) => {
  const { data: categorias, isLoading: loadingCategorias } = useCategorias();
  const [searchInput, setSearchInput] = useState('');

  // Debounce del texto de búsqueda
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(searchInput);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput, onSearchChange]);

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onCategoryChange(value === '' ? undefined : Number(value));
  };

  return (
    <div className="flex flex-col sm:flex-row gap-3">
      {/* Selector de categoría */}
      <div className="flex-1 sm:max-w-xs">
        <label htmlFor="categoria-select" className="sr-only">
          Filtrar por categoría
        </label>
        <select
          id="categoria-select"
          onChange={handleCategoryChange}
          disabled={loadingCategorias}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <option value="">Todas las categorías</option>
          {categorias?.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nombre}
            </option>
          ))}
        </select>
      </div>

      {/* Input de búsqueda */}
      <div className="flex-1">
        <label htmlFor="search-input" className="sr-only">
          Buscar producto
        </label>
        <input
          id="search-input"
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Buscar producto..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};

export default CatalogoFilters;
