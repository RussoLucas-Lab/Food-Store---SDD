/**
 * CreateOrderButton — Botón para crear el pedido desde el carrito.
 *
 * - Disabled si el carrito está vacío o no hay dirección seleccionada
 * - Muestra loading spinner mientras espera respuesta
 * - En éxito: clearCart y navega a /pedidos/{id}
 * - En error: muestra mensaje de error
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '../../../shared/stores/cartStore';
import { usePaymentStore } from '../../../shared/stores/paymentStore';
import { createPedido } from '../services/pedidoClient';

interface CreateOrderButtonProps {
  /** ID de la dirección seleccionada (null si no hay selección) */
  selectedDirectionId: number | null;
}

const CreateOrderButton: React.FC<CreateOrderButtonProps> = ({ selectedDirectionId }) => {
  const navigate = useNavigate();
  const items = useCartStore((s) => s.items);
  const getCartDTO = useCartStore((s) => s.getCartDTO);
  const setPedidoId = usePaymentStore((s) => s.setPedidoId);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isDisabled = items.length === 0 || selectedDirectionId === null || loading;

  const handleCreateOrder = async () => {
    if (isDisabled) return;
    setLoading(true);
    setError(null);

    try {
      const dto = getCartDTO(selectedDirectionId!);
      const pedido = await createPedido(dto);
      // Tarea 6.2: asociar el pedido al paymentStore antes de redirigir
      setPedidoId(String(pedido.id));
      // Tarea 6.1: redirigir a la página de pago en lugar de la confirmación directa
      navigate(`/pedidos/${pedido.id}/pago`);
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: string }).message)
          : 'Error al crear el pedido. Intente nuevamente.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-2">
      {error && (
        <p className="text-sm text-red-600 bg-red-50 p-2 rounded" role="alert">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={handleCreateOrder}
        disabled={isDisabled}
        aria-busy={loading}
        className={[
          'w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors',
          isDisabled
            ? 'bg-gray-300 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700 active:bg-green-800',
        ].join(' ')}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8z"
              />
            </svg>
            Creando pedido...
          </span>
        ) : (
          'Confirmar Pedido'
        )}
      </button>
    </div>
  );
};

export default CreateOrderButton;
