/**
 * SkeletonDetail — Skeleton para el layout de detalle de producto.
 *
 * Layout de 2 columnas: imagen (izquierda) + controles (derecha).
 */

import React from 'react';

const SkeletonDetail: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Columna imagen */}
        <div className="w-full h-80 bg-gray-200 rounded-xl" />

        {/* Columna controles */}
        <div className="space-y-4">
          {/* Nombre */}
          <div className="h-7 bg-gray-200 rounded w-3/4" />
          {/* Precio */}
          <div className="h-6 bg-gray-200 rounded w-1/4" />
          {/* Descripción */}
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-full" />
            <div className="h-4 bg-gray-200 rounded w-5/6" />
            <div className="h-4 bg-gray-200 rounded w-2/3" />
          </div>
          {/* Ingredientes */}
          <div className="space-y-2 pt-2">
            <div className="h-4 bg-gray-200 rounded w-1/3" />
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-4 bg-gray-200 rounded w-1/2" />
            ))}
          </div>
          {/* Cantidad + botón */}
          <div className="flex gap-4 pt-4">
            <div className="h-10 bg-gray-200 rounded w-24" />
            <div className="h-10 bg-gray-200 rounded flex-1" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkeletonDetail;
