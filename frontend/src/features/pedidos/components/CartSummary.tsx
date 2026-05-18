/**
 * CartSummary — Resumen del carrito con subtotal, envío y total.
 *
 * Lee el total del cartStore y calcula el costo de envío.
 */

import React from 'react';
import { useCartStore } from '../../../shared/stores/cartStore';

// Constante de costo de envío (en esta versión sin cargo)
const COSTO_ENVIO = 0;

const CartSummary: React.FC = () => {
  const getTotal = useCartStore((s) => s.getTotal);
  const subtotal = getTotal();
  const total = subtotal + COSTO_ENVIO;

  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-2" data-testid="cart-summary">
      <h3 className="font-semibold text-gray-900 mb-3">Resumen del pedido</h3>

      <div className="flex justify-between text-sm text-gray-600">
        <span>Subtotal</span>
        <span>${subtotal.toFixed(2)}</span>
      </div>

      <div className="flex justify-between text-sm text-gray-600">
        <span>Costo de envío</span>
        <span>{COSTO_ENVIO === 0 ? 'Gratis' : `$${COSTO_ENVIO.toFixed(2)}`}</span>
      </div>

      <div className="border-t pt-2 mt-2 flex justify-between font-semibold text-gray-900">
        <span>Total</span>
        <span>${total.toFixed(2)}</span>
      </div>
    </div>
  );
};

export default CartSummary;
