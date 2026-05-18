/**
 * EstadoActions — Muestra botones de transición válidos según el estado actual
 * y el rol del usuario. Solicita motivo obligatorio al cancelar.
 */

import React, { useState } from 'react';

// FSM: transiciones válidas por estado (espejo del backend, D1/D3)
const TRANSICIONES_POR_ESTADO: Record<string, string[]> = {
  PENDIENTE:      ['CANCELADO'],
  CONFIRMADO:     ['EN_PREPARACION', 'CANCELADO'],
  EN_PREPARACION: ['EN_CAMINO', 'CANCELADO'],
  EN_CAMINO:      ['ENTREGADO'],
  ENTREGADO:      [],
  CANCELADO:      [],
};

// Autorización por rol y transición (espejo del backend, D3)
const AUTORIZACION: Record<string, Record<string, string[]>> = {
  PENDIENTE: {
    CANCELADO: ['CLIENT', 'PEDIDOS', 'ADMIN'],
  },
  CONFIRMADO: {
    EN_PREPARACION: ['PEDIDOS', 'ADMIN'],
    CANCELADO:      ['PEDIDOS', 'ADMIN'],
  },
  EN_PREPARACION: {
    EN_CAMINO: ['PEDIDOS', 'ADMIN'],
    CANCELADO: ['ADMIN'],
  },
  EN_CAMINO: {
    ENTREGADO: ['PEDIDOS', 'ADMIN'],
  },
};

const ETIQUETA_TRANSICION: Record<string, string> = {
  EN_PREPARACION: 'Iniciar preparación',
  EN_CAMINO:      'Marcar en camino',
  ENTREGADO:      'Marcar como entregado',
  CANCELADO:      'Cancelar pedido',
};

interface EstadoActionsProps {
  estadoActual: string;
  rol: string;  // 'CLIENT' | 'PEDIDOS' | 'ADMIN'
  onTransicion: (nuevoEstado: string, motivo?: string) => void;
  isLoading?: boolean;
}

const EstadoActions: React.FC<EstadoActionsProps> = ({
  estadoActual,
  rol,
  onTransicion,
  isLoading = false,
}) => {
  const [showMotivoDialog, setShowMotivoDialog] = useState(false);
  const [motivo, setMotivo] = useState('');
  const [pendingEstado, setPendingEstado] = useState<string | null>(null);

  const rolUpper = rol.toUpperCase();

  // Filtrar transiciones válidas para este estado y rol
  const transicionesPermitidas = (TRANSICIONES_POR_ESTADO[estadoActual] ?? []).filter(
    (destino) => {
      const rolesAutorizados = AUTORIZACION[estadoActual]?.[destino] ?? [];
      return rolesAutorizados.includes(rolUpper);
    }
  );

  if (transicionesPermitidas.length === 0) {
    return null;
  }

  const handleClick = (destino: string) => {
    if (destino === 'CANCELADO') {
      setPendingEstado(destino);
      setMotivo('');
      setShowMotivoDialog(true);
    } else {
      onTransicion(destino);
    }
  };

  const handleConfirmCancelacion = () => {
    if (!motivo.trim()) return;
    setShowMotivoDialog(false);
    onTransicion(pendingEstado!, motivo.trim());
    setMotivo('');
    setPendingEstado(null);
  };

  const handleCancelDialog = () => {
    setShowMotivoDialog(false);
    setMotivo('');
    setPendingEstado(null);
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-2">
        {transicionesPermitidas.map((destino) => (
          <button
            key={destino}
            onClick={() => handleClick(destino)}
            disabled={isLoading}
            className={`px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 ${
              destino === 'CANCELADO'
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {ETIQUETA_TRANSICION[destino] ?? destino}
          </button>
        ))}
      </div>

      {/* Diálogo de motivo para cancelación */}
      {showMotivoDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Cancelar pedido</h3>
            <p className="text-sm text-gray-600 mb-4">
              Por favor indicá el motivo de la cancelación (obligatorio).
            </p>
            <textarea
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              rows={3}
              placeholder="Motivo de cancelación..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400 mb-4"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={handleCancelDialog}
                className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Volver
              </button>
              <button
                onClick={handleConfirmCancelacion}
                disabled={!motivo.trim()}
                className="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                Confirmar cancelación
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EstadoActions;
