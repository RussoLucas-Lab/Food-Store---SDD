/**
 * SkeletonCard — Tarjeta placeholder animada para loading de productos.
 *
 * Muestra una tarjeta gris con `animate-pulse` mientras carga el contenido real.
 */

import React from 'react';

const SkeletonCard: React.FC = () => {
  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm animate-pulse">
      {/* Imagen placeholder */}
      <div className="w-full h-48 bg-gray-200" />

      {/* Contenido placeholder */}
      <div className="p-4 space-y-3">
        {/* Nombre */}
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        {/* Descripción */}
        <div className="h-3 bg-gray-200 rounded w-full" />
        <div className="h-3 bg-gray-200 rounded w-2/3" />
        {/* Precio + botón */}
        <div className="flex justify-between items-center pt-2">
          <div className="h-5 bg-gray-200 rounded w-1/4" />
          <div className="h-8 bg-gray-200 rounded w-1/3" />
        </div>
      </div>
    </div>
  );
};

export default SkeletonCard;
