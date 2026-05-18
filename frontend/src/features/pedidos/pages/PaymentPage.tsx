/**
 * PaymentPage — Página de pago con MercadoPago Checkout Bricks.
 *
 * Flujo:
 * 1. Lee pedidoId del paymentStore (seteado por CheckoutPage antes de redirigir)
 * 2. Muestra CardPayment Brick de @mercadopago/sdk-react
 * 3. En submit del Brick: llama createPago → actualiza paymentStore → limpia carrito → navega a /pedidos/{id}
 * 4. En error: muestra toast de error, permite reintento sin salir de la página
 *
 * Seguridad (PCI DSS SAQ-A):
 * - Los datos de tarjeta NUNCA pasan por el servidor
 * - El token generado por MP SDK es lo único que se envía al backend
 */

import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { initMercadoPago, CardPayment } from '@mercadopago/sdk-react';
import { usePaymentStore } from '../../../shared/stores/paymentStore';
import { useCartStore } from '../../../shared/stores/cartStore';
import { createPago } from '../services/pagoClient';

initMercadoPago(import.meta.env.VITE_MP_PUBLIC_KEY as string);

// ── Component ─────────────────────────────────────────────────────────────────

const PaymentPage: React.FC = () => {
  const navigate = useNavigate();
  const { id: pedidoIdFromUrl } = useParams<{ id: string }>();

  const pedidoId = usePaymentStore((s) => s.pedidoId);
  const storeError = usePaymentStore((s) => s.error);
  const setPaymentResult = usePaymentStore((s) => s.setPaymentResult);
  const setStoreError = usePaymentStore((s) => s.setError);
  const clearCart = useCartStore((s) => s.clearCart);
  const getTotal = useCartStore((s) => s.getTotal);

  const activePedidoId = pedidoId || pedidoIdFromUrl || null;

  useEffect(() => {
    if (!activePedidoId) {
      navigate('/checkout', { replace: true });
    }
  }, [activePedidoId, navigate]);

  const total = getTotal();

  const handleBrickSubmit = async (brickData: {
    token: string;
    installments: number;
    payment_method_id: string;
    issuer_id?: string;
  }) => {
    if (!activePedidoId) return;

    try {
      const pago = await createPago({
        pedido_id: parseInt(activePedidoId, 10),
        token: brickData.token,
        installments: brickData.installments,
        payment_method_id: brickData.payment_method_id,
        issuer_id: brickData.issuer_id,
      });

      setPaymentResult(pago.mp_status, pago.mp_payment_id || '');
      clearCart();
      navigate(`/pedidos/${activePedidoId}`);
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: string }).message)
          : 'Error al procesar el pago. Intente nuevamente.';
      setStoreError(message);
    }
  };

  if (!activePedidoId) {
    return null;
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-8" data-testid="payment-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Pago con tarjeta</h1>
        <p className="text-sm text-gray-500 mt-1">Pedido #{activePedidoId}</p>
      </div>

      <div
        className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6"
        data-testid="pedido-summary"
      >
        <h2 className="text-sm font-semibold text-gray-700 mb-2">
          Resumen del pedido
        </h2>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Total a pagar:</span>
          <span className="text-xl font-bold text-gray-900">
            ${total.toFixed(2)}
          </span>
        </div>
      </div>

      {storeError && (
        <div
          className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-4"
          role="alert"
          data-testid="payment-error"
        >
          <p className="font-medium">Error al procesar el pago</p>
          <p className="text-sm mt-1">{storeError}</p>
          <p className="text-sm mt-2 text-red-600">
            Podés reintentar con el mismo formulario.
          </p>
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <CardPayment
          initialization={{ amount: total }}
          onSubmit={handleBrickSubmit}
          onError={(error) => setStoreError(error.message)}
        />
      </div>

      <button
        type="button"
        onClick={() => navigate('/checkout')}
        className="w-full py-2 mt-4 text-sm text-gray-500 hover:text-gray-700 transition-colors"
      >
        ← Volver al checkout
      </button>
    </div>
  );
};

export default PaymentPage;
