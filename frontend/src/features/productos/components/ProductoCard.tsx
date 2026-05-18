/**
 * ProductoCard — Tarjeta de producto para el catálogo.
 *
 * Muestra nombre, precio formateado en ARS, imagen o placeholder,
 * y botón "Agregar" que llama cartStore.addItem y muestra un toast.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useCartStore } from '@/shared/stores/cartStore';
import { toast } from '@/shared/hooks/useToast';
import type { ProductoListItem } from '../services/productosApi';

interface ProductoCardProps {
  producto: ProductoListItem;
}

const formatPrecio = (precio: number): string =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(precio);

const ProductoCard: React.FC<ProductoCardProps> = ({ producto }) => {
  const addItem = useCartStore((s) => s.addItem);

  const handleAgregar = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    addItem(
      { id: producto.id, nombre: producto.nombre, precio: producto.precio },
      1
    );
    toast('Producto agregado al carrito', 'success');
  };

  return (
    <Link
      to={`/productos/${producto.id}`}
      className="group bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col"
    >
      {/* Imagen */}
      {producto.imagen_url ? (
        <img
          src={producto.imagen_url}
          alt={producto.nombre}
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="w-full h-48 bg-gray-100 flex items-center justify-center text-gray-400">
          <svg
            className="w-16 h-16"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      )}

      {/* Contenido */}
      <div className="p-4 flex flex-col flex-1">
        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2">
          {producto.nombre}
        </h3>

        {producto.descripcion && (
          <p className="text-sm text-gray-500 mt-1 line-clamp-2 flex-1">
            {producto.descripcion}
          </p>
        )}

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
          <span className="text-lg font-bold text-gray-900">
            {formatPrecio(producto.precio)}
          </span>

          {producto.disponible && producto.stock > 0 ? (
            <button
              onClick={handleAgregar}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              aria-label={`Agregar ${producto.nombre} al carrito`}
            >
              Agregar
            </button>
          ) : (
            <span className="text-xs text-gray-400 font-medium">Sin stock</span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default ProductoCard;
