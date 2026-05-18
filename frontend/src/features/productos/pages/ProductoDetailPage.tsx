/**
 * ProductoDetailPage — Detalle de un producto.
 *
 * Ruta: /productos/:id
 * Muestra imagen, nombre, precio, ingredientes y permite agregar al carrito
 * con cantidad y personalizaciones.
 */

import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useProducto } from '../hooks/useProducto';
import { useCartStore } from '@/shared/stores/cartStore';
import { useUiStore } from '@/shared/stores/uiStore';
import { toast } from '@/shared/hooks/useToast';
import SkeletonDetail from '@/shared/components/atoms/SkeletonDetail';
import IngredienteSelector from '../components/IngredienteSelector';

const formatPrecio = (precio: number): string =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(precio);

const ProductoDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const productoId = id ? parseInt(id, 10) : null;

  const { data: producto, isLoading, error } = useProducto(productoId);
  const addItem = useCartStore((s) => s.addItem);
  const setCartOpen = useUiStore((s) => s.setCartOpen);

  const [cantidad, setCantidad] = useState(1);
  const [excluidos, setExcluidos] = useState<number[]>([]);

  const handleAgregar = () => {
    if (!producto) return;
    addItem(
      { id: producto.id, nombre: producto.nombre, precio: producto.precio },
      cantidad,
      excluidos
    );
    toast(`${producto.nombre} agregado al carrito`, 'success');
    setCartOpen(true);
  };

  if (isLoading) {
    return <SkeletonDetail />;
  }

  if (error || !producto) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center px-4">
        <div className="text-5xl mb-4">😕</div>
        <h1 className="text-2xl font-bold text-gray-700 mb-2">
          Producto no encontrado
        </h1>
        <p className="text-gray-500 mb-6">
          El producto que buscás no existe o fue eliminado.
        </p>
        <Link
          to="/productos"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          ← Volver al catálogo
        </Link>
      </div>
    );
  }

  const disponible = producto.disponible && producto.stock > 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-500 mb-6">
        <Link to="/productos" className="hover:text-blue-600">
          Catálogo
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900 font-medium">{producto.nombre}</span>
      </nav>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Imagen */}
        <div className="rounded-xl overflow-hidden bg-gray-100">
          {producto.imagen_url ? (
            <img
              src={producto.imagen_url}
              alt={producto.nombre}
              className="w-full h-80 object-cover"
            />
          ) : (
            <div className="w-full h-80 flex items-center justify-center text-gray-300">
              <svg
                className="w-24 h-24"
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
        </div>

        {/* Info */}
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{producto.nombre}</h1>
            <p className="text-2xl font-bold text-blue-600 mt-1">
              {formatPrecio(producto.precio)}
            </p>
          </div>

          {producto.descripcion && (
            <p className="text-gray-600 text-sm leading-relaxed">
              {producto.descripcion}
            </p>
          )}

          {/* Stock */}
          <div>
            {disponible ? (
              <span className="inline-block text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded-full">
                Disponible ({producto.stock} en stock)
              </span>
            ) : (
              <span className="inline-block text-xs font-medium text-red-700 bg-red-100 px-2 py-1 rounded-full">
                Sin stock
              </span>
            )}
          </div>

          {/* Ingredientes */}
          {producto.ingredientes && producto.ingredientes.length > 0 && (
            <IngredienteSelector
              ingredientes={producto.ingredientes}
              onChange={setExcluidos}
            />
          )}

          {/* Cantidad */}
          {disponible && (
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700">Cantidad:</span>
              <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                <button
                  onClick={() => setCantidad((c) => Math.max(1, c - 1))}
                  className="px-3 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 font-bold transition-colors"
                  aria-label="Reducir cantidad"
                >
                  −
                </button>
                <span className="px-4 py-2 text-gray-900 font-semibold min-w-[3rem] text-center">
                  {cantidad}
                </span>
                <button
                  onClick={() => setCantidad((c) => Math.min(producto.stock, c + 1))}
                  className="px-3 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 font-bold transition-colors"
                  aria-label="Aumentar cantidad"
                >
                  +
                </button>
              </div>
            </div>
          )}

          {/* Botón agregar */}
          <button
            onClick={handleAgregar}
            disabled={!disponible}
            className="w-full py-3 px-6 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {disponible ? 'Agregar al carrito' : 'Sin stock'}
          </button>

          {/* Link volver */}
          <Link
            to="/productos"
            className="block text-center text-sm text-blue-600 hover:underline"
          >
            ← Volver al catálogo
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ProductoDetailPage;
