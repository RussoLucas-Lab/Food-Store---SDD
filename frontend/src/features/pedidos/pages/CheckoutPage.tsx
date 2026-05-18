/**
 * CheckoutPage — Página de checkout del carrito.
 *
 * Layout 2 columnas:
 * - Izquierda: CartItemList (ítems del carrito)
 * - Derecha: CartSummary + DirectionSelector + CreateOrderButton
 *
 * Si el carrito está vacío, muestra mensaje con link al catálogo.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCartStore } from '../../../shared/stores/cartStore';
import CartItemList from '../components/CartItemList';
import CartSummary from '../components/CartSummary';
import DirectionSelector from '../components/DirectionSelector';
import CreateOrderButton from '../components/CreateOrderButton';

const CheckoutPage: React.FC = () => {
  const items = useCartStore((s) => s.items);
  const [selectedDirectionId, setSelectedDirectionId] = useState<number | null>(null);

  // Carrito vacío
  if (items.length === 0) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center" data-testid="empty-cart">
        <h2 className="text-2xl font-bold text-gray-700 mb-4">
          Tu carrito está vacío
        </h2>
        <p className="text-gray-500 mb-6">
          Agregá productos antes de continuar con el checkout.
        </p>
        <Link
          to="/productos"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Ir al catálogo
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8" data-testid="checkout-page">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Checkout</h1>
        <Link
          to="/productos"
          className="text-blue-600 hover:underline text-sm font-medium"
        >
          ← Seguir comprando
        </Link>
      </div>

      {/* Layout 2 columnas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Columna izquierda: lista de ítems */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Ítems del carrito
          </h2>
          <CartItemList />
        </div>

        {/* Columna derecha: resumen + dirección + botón */}
        <div className="space-y-6">
          <CartSummary />

          <DirectionSelector
            selectedId={selectedDirectionId}
            onSelect={setSelectedDirectionId}
          />

          <CreateOrderButton selectedDirectionId={selectedDirectionId} />
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
