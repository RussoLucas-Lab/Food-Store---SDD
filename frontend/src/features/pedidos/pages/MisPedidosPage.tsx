/**
 * MisPedidosPage — Vista de "Mis Pedidos" para el cliente (rol CLIENT).
 *
 * Funcionalidades:
 * - Lista de pedidos del cliente con estado, total y fecha
 * - Detalle expandible con línea de tiempo de estados
 * - Cancelación de pedidos en PENDIENTE (con motivo obligatorio)
 */

import React, { useState } from 'react';
import { useMisPedidos, usePedidoDetalle, useUpdateEstado } from '../hooks/usePedidos';
import EstadoBadge from '../components/EstadoBadge';
import EstadoTimeline from '../components/EstadoTimeline';
import EstadoActions from '../components/EstadoActions';

const MisPedidosPage: React.FC = () => {
  const [skip, setSkip] = useState(0);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const LIMIT = 10;

  const { data: pedidos, isLoading, isError } = useMisPedidos(skip, LIMIT);
  const { data: detalleData, isLoading: detalleLoading } = usePedidoDetalle(selectedId);
  const updateEstado = useUpdateEstado();

  const handleTransicion = (nuevoEstado: string, motivo?: string) => {
    if (!selectedId) return;
    updateEstado.mutate(
      { pedidoId: selectedId, nuevoEstado, motivo },
      {
        onError: (err) => {
          alert(`Error: ${err.message}`);
        },
      }
    );
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mis Pedidos</h1>

      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4 text-red-700 text-sm">
          Error al cargar tus pedidos.
        </div>
      )}

      <div className="flex gap-6">
        {/* Lista de pedidos */}
        <div className="flex-1 min-w-0">
          {isLoading ? (
            <div className="text-gray-500 text-sm py-8 text-center">Cargando pedidos...</div>
          ) : !pedidos || pedidos.length === 0 ? (
            <div className="text-gray-500 py-8 text-center">
              <div className="text-4xl mb-3">📦</div>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Todavía no hiciste ningún pedido
              </p>
              <p className="text-sm text-gray-400 mb-4">
                Explorá el catálogo y hacé tu primer pedido.
              </p>
              <a
                href="/productos"
                className="inline-block bg-blue-600 text-white px-5 py-2 rounded-lg font-semibold text-sm hover:bg-blue-700 transition-colors"
              >
                Ver catálogo
              </a>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {pedidos.map((pedido) => (
                <div
                  key={pedido.id}
                  onClick={() => setSelectedId(pedido.id === selectedId ? null : pedido.id)}
                  className={`border rounded-lg p-4 cursor-pointer hover:border-blue-400 transition-colors ${
                    selectedId === pedido.id
                      ? 'border-blue-400 bg-blue-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">Pedido #{pedido.id}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(pedido.creado_en).toLocaleDateString('es-AR', {
                          day: '2-digit',
                          month: 'long',
                          year: 'numeric',
                        })}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <EstadoBadge estado={pedido.estado} />
                      <span className="text-sm font-semibold text-gray-900">
                        ${pedido.total.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Paginación */}
          {pedidos && (
            <div className="flex justify-between items-center mt-4">
              <button
                onClick={() => setSkip(Math.max(0, skip - LIMIT))}
                disabled={skip === 0}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-40 hover:bg-gray-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setSkip(skip + LIMIT)}
                disabled={pedidos.length < LIMIT}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-40 hover:bg-gray-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </div>

        {/* Panel de detalle */}
        {selectedId && (
          <div className="w-80 flex-shrink-0">
            <div className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm sticky top-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Detalle #{selectedId}
              </h2>

              {detalleLoading ? (
                <div className="text-gray-500 text-sm">Cargando...</div>
              ) : detalleData ? (
                <>
                  <div className="mb-3">
                    <EstadoBadge estado={detalleData.estado} />
                  </div>

                  <div className="mb-3 text-sm text-gray-700">
                    <span className="font-medium">Total: </span>
                    ${detalleData.total.toFixed(2)}
                  </div>

                  {/* Acciones (solo PENDIENTE para CLIENT) */}
                  {detalleData.estado === 'PENDIENTE' && (
                    <div className="mb-4">
                      <EstadoActions
                        estadoActual={detalleData.estado}
                        rol="CLIENT"
                        onTransicion={handleTransicion}
                        isLoading={updateEstado.isPending}
                      />
                      {updateEstado.isError && (
                        <p className="text-red-600 text-xs mt-2">
                          {String(updateEstado.error)}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Línea de tiempo */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Historial del pedido
                    </h3>
                    <EstadoTimeline historial={detalleData.historial} />
                  </div>
                </>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MisPedidosPage;
