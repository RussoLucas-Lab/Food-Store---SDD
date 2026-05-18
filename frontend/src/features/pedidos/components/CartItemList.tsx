/**
 * CartItemList — Lista de ítems del carrito.
 *
 * Lee los items del cartStore y permite modificar cantidades o quitar ítems.
 * Usa selectores para evitar re-renders innecesarios.
 */

import React from 'react';
import { useCartStore } from '../../../shared/stores/cartStore';

const CartItemList: React.FC = () => {
  const items = useCartStore((s) => s.items);
  const updateQuantity = useCartStore((s) => s.updateQuantity);
  const removeItem = useCartStore((s) => s.removeItem);

  if (items.length === 0) {
    return (
      <p className="text-gray-500 text-center py-4">
        No hay ítems en el carrito.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-gray-200" data-testid="cart-item-list">
      {items.map((item) => (
        <li key={item.producto_id} className="py-4 flex items-start gap-4">
          {/* Info del producto */}
          <div className="flex-1">
            <p className="font-medium text-gray-900">{item.producto_nombre}</p>
            <p className="text-sm text-gray-500">
              ${item.precio.toFixed(2)} c/u
            </p>

            {/* Ingredientes excluidos */}
            {item.personalizacion.excluidos.length > 0 && (
              <p className="text-xs text-orange-600 mt-1">
                Sin ingredientes: {item.personalizacion.excluidos.join(', ')}
              </p>
            )}
          </div>

          {/* Controles de cantidad */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              aria-label={`Disminuir cantidad de ${item.producto_nombre}`}
              onClick={() => updateQuantity(item.producto_id, item.cantidad - 1)}
              className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-100"
            >
              −
            </button>

            <span className="w-6 text-center text-sm font-medium">
              {item.cantidad}
            </span>

            <button
              type="button"
              aria-label={`Aumentar cantidad de ${item.producto_nombre}`}
              onClick={() => updateQuantity(item.producto_id, item.cantidad + 1)}
              className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-100"
            >
              +
            </button>
          </div>

          {/* Subtotal del ítem */}
          <div className="text-sm font-semibold text-gray-900 w-20 text-right">
            ${(item.precio * item.cantidad).toFixed(2)}
          </div>

          {/* Quitar ítem */}
          <button
            type="button"
            aria-label={`Quitar ${item.producto_nombre} del carrito`}
            onClick={() => removeItem(item.producto_id)}
            className="text-red-500 hover:text-red-700 text-sm font-medium ml-2"
          >
            Quitar
          </button>
        </li>
      ))}
    </ul>
  );
};

export default CartItemList;
