/**
 * GestionPedidosPage — Panel de gestión de pedidos para PEDIDOS/ADMIN.
 *
 * Funcionalidades:
 * - Tabla de pedidos con filtros (estado, fecha) y paginación
 * - Detalle expandible con historial y acciones de transición
 */

import React, { useState } from 'react';
import { useGestionPedidos, usePedidoDetalle, useUpdateEstado } from '../hooks/usePedidos';
import EstadoBadge from '../components/EstadoBadge';
import EstadoTimeline from '../components/EstadoTimeline';
import EstadoActions from '../components/EstadoActions';
import PedidoFilters, { type PedidoFiltros } from '../components/PedidoFilters';
import { useAuth } from '@/shared/context/AuthContext';
import type { ListGestionFilters } from '../services/pedidoClient';

const GestionPedidosPage: React.FC = () => {
  const { user } = useAuth();
  const [filtros, setFiltros] = useState<PedidoFiltros>({});
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [skip, setSkip] = useState(0);
  const LIMIT = 20;

  // Construir filtros para la query
  const queryFiltros: ListGestionFilters = {
    estado: filtros.estado,
    fecha_desde: filtros.fechaDesde,
    fecha_hasta: filtros.fechaHasta,
    skip,
    limit: LIMIT,
  };

  const { data: pedidos, isLoading, isError, error } = useGestionPedidos(queryFiltros);
  const { data: detalleData, isLoading: detalleLoading } = usePedidoDetalle(selectedId);
  const updateEstado = useUpdateEstado();

  const rolUsuario = (() => {
    if (!user) return 'GUEST';
    if (user.role === 'ADMIN') return 'ADMIN';
    return 'PEDIDOS';
  })();

  const handleFiltroChange = (nuevosFiltros: PedidoFiltros) => {
    setFiltros(nuevosFiltros);
    setSkip(0);
    setSelectedId(null);
  };

  const handleTransicion = (pedidoId: number, nuevoEstado: string, motivo?: string) => {
    updateEstado.mutate(
      { pedidoId, nuevoEstado, motivo },
      {
        onError: (err) => {
          alert(`Error al cambiar el estado: ${err.message}`);
        },
      }
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Gestión de Pedidos</h1>

      {/* Filtros */}
      <div className="mb-6">
        <PedidoFilters filtros={filtros} onChange={handleFiltroChange} />
      </div>

      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4 text-red-700 text-sm">
          Error al cargar pedidos: {String(error)}
        </div>
      )}

      <div className="flex gap-6">
        {/* Tabla de pedidos */}
        <div className="flex-1 min-w-0">
          {isLoading ? (
            <div className="text-gray-500 text-sm py-8 text-center">Cargando pedidos...</div>
          ) : !pedidos || pedidos.length === 0 ? (
            <div className="text-gray-500 text-sm py-8 text-center">
              No hay pedidos con los filtros seleccionados.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {pedidos.map((pedido) => (
                    <tr
                      key={pedido.id}
                      onClick={() => setSelectedId(pedido.id === selectedId ? null : pedido.id)}
                      className={`cursor-pointer hover:bg-blue-50 transition-colors ${
                        selectedId === pedido.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <td className="px-4 py-3 text-sm font-mono text-gray-900">#{pedido.id}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{pedido.cliente_id}</td>
                      <td className="px-4 py-3">
                        <EstadoBadge estado={pedido.estado} />
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        ${pedido.total.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(pedido.creado_en).toLocaleDateString('es-AR')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Paginación */}
          <div className="flex justify-between items-center mt-4">
            <button
              onClick={() => setSkip(Math.max(0, skip - LIMIT))}
              disabled={skip === 0}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-40 hover:bg-gray-50"
            >
              Anterior
            </button>
            <span className="text-sm text-gray-600">
              Mostrando {skip + 1}–{skip + (pedidos?.length ?? 0)}
            </span>
            <button
              onClick={() => setSkip(skip + LIMIT)}
              disabled={!pedidos || pedidos.length < LIMIT}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-40 hover:bg-gray-50"
            >
              Siguiente
            </button>
          </div>
        </div>

        {/* Panel de detalle */}
        {selectedId && (
          <div className="w-96 flex-shrink-0">
            <div className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Pedido #{selectedId}
              </h2>

              {detalleLoading ? (
                <div className="text-gray-500 text-sm">Cargando detalle...</div>
              ) : detalleData ? (
                <>
                  <div className="mb-4">
                    <EstadoBadge estado={detalleData.estado} />
                  </div>

                  {/* Acciones */}
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Acciones</h3>
                    <EstadoActions
                      estadoActual={detalleData.estado}
                      rol={rolUsuario}
                      onTransicion={(nuevoEstado, motivo) =>
                        handleTransicion(selectedId, nuevoEstado, motivo)
                      }
                      isLoading={updateEstado.isPending}
                    />
                    {updateEstado.isError && (
                      <p className="text-red-600 text-xs mt-2">
                        {String(updateEstado.error)}
                      </p>
                    )}
                  </div>

                  {/* Línea de tiempo */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Historial</h3>
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

export default GestionPedidosPage;
