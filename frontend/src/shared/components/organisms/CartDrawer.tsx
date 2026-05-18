/**
 * CartDrawer — Panel lateral del carrito de compras.
 *
 * - Controlado por uiStore.cartOpen (sin props)
 * - Overlay oscuro + panel lateral derecho
 * - transición CSS translate para abrir/cerrar
 * - Lista de ítems con controles +/− y botón eliminar
 * - Footer: total + CTA "Ir al checkout"
 * - Empty state si el carrito está vacío
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '@/shared/stores/cartStore';
import { useUiStore } from '@/shared/stores/uiStore';

const formatPrecio = (precio: number): string =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(precio);

const CartDrawer: React.FC = () => {
  const navigate = useNavigate();

  const cartOpen = useUiStore((s) => s.cartOpen);
  const setCartOpen = useUiStore((s) => s.setCartOpen);

  const items = useCartStore((s) => s.items);
  const updateQuantity = useCartStore((s) => s.updateQuantity);
  const removeItem = useCartStore((s) => s.removeItem);
  const getTotal = useCartStore((s) => s.getTotal);

  const total = getTotal();

  const handleCheckout = () => {
    setCartOpen(false);
    navigate('/checkout');
  };

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black transition-opacity duration-300 ${
          cartOpen ? 'opacity-50 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setCartOpen(false)}
        aria-hidden="true"
      />

      {/* Panel lateral */}
      <div
        role="dialog"
        aria-label="Carrito de compras"
        aria-modal="true"
        className={`fixed top-0 right-0 h-full w-80 sm:w-96 bg-white shadow-2xl z-50 flex flex-col transition-transform duration-300 ${
          cartOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">
            Carrito
            {items.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({items.length} {items.length === 1 ? 'ítem' : 'ítems'})
              </span>
            )}
          </h2>
          <button
            onClick={() => setCartOpen(false)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Cerrar carrito"
          >
            ✕
          </button>
        </div>

        {/* Contenido */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="text-5xl mb-4">🛒</div>
              <p className="text-gray-600 font-medium">Tu carrito está vacío</p>
              <p className="text-sm text-gray-400 mt-1">
                Explorá el catálogo y agregá productos.
              </p>
              <button
                onClick={() => {
                  setCartOpen(false);
                  navigate('/productos');
                }}
                className="mt-4 text-sm text-blue-600 hover:underline"
              >
                Ver catálogo →
              </button>
            </div>
          ) : (
            <ul className="space-y-4">
              {items.map((item) => (
                <li
                  key={item.producto_id}
                  className="flex items-start gap-3 pb-4 border-b border-gray-100 last:border-0"
                >
                  {/* Nombre y precio unitario */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.producto_nombre}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {formatPrecio(item.precio)} c/u
                    </p>
                    {item.personalizacion.excluidos.length > 0 && (
                      <p className="text-xs text-amber-600 mt-0.5">
                        Sin: {item.personalizacion.excluidos.join(', ')}
                      </p>
                    )}
                  </div>

                  {/* Controles de cantidad */}
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <button
                      onClick={() =>
                        updateQuantity(item.producto_id, item.cantidad - 1)
                      }
                      className="w-7 h-7 flex items-center justify-center border border-gray-300 rounded-md text-gray-600 hover:bg-gray-100 transition-colors text-sm font-bold"
                      aria-label="Reducir cantidad"
                    >
                      −
                    </button>
                    <span className="w-7 text-center text-sm font-semibold text-gray-900">
                      {item.cantidad}
                    </span>
                    <button
                      onClick={() =>
                        updateQuantity(item.producto_id, item.cantidad + 1)
                      }
                      className="w-7 h-7 flex items-center justify-center border border-gray-300 rounded-md text-gray-600 hover:bg-gray-100 transition-colors text-sm font-bold"
                      aria-label="Aumentar cantidad"
                    >
                      +
                    </button>
                  </div>

                  {/* Subtotal + eliminar */}
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <span className="text-sm font-semibold text-gray-900">
                      {formatPrecio(item.precio * item.cantidad)}
                    </span>
                    <button
                      onClick={() => removeItem(item.producto_id)}
                      className="text-xs text-red-400 hover:text-red-600 transition-colors"
                      aria-label={`Eliminar ${item.producto_nombre} del carrito`}
                    >
                      ×
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="px-4 py-4 border-t border-gray-200 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-base font-semibold text-gray-900">Total</span>
              <span className="text-lg font-bold text-gray-900">
                {formatPrecio(total)}
              </span>
            </div>
            <button
              onClick={handleCheckout}
              className="w-full py-3 px-6 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Ir al checkout →
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default CartDrawer;
