/**
 * PedidoFilters — Filtros para el listado de gestión de pedidos.
 *
 * Permite seleccionar un estado y un rango de fechas.
 */

import React from 'react';

const ESTADOS = [
  { value: '', label: 'Todos los estados' },
  { value: 'PENDIENTE', label: 'Pendiente' },
  { value: 'CONFIRMADO', label: 'Confirmado' },
  { value: 'EN_PREPARACION', label: 'En preparación' },
  { value: 'EN_CAMINO', label: 'En camino' },
  { value: 'ENTREGADO', label: 'Entregado' },
  { value: 'CANCELADO', label: 'Cancelado' },
];

export interface PedidoFiltros {
  estado?: string;
  fechaDesde?: string;
  fechaHasta?: string;
}

interface PedidoFiltersProps {
  filtros: PedidoFiltros;
  onChange: (filtros: PedidoFiltros) => void;
}

const PedidoFilters: React.FC<PedidoFiltersProps> = ({ filtros, onChange }) => {
  const handleEstado = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({ ...filtros, estado: e.target.value || undefined });
  };

  const handleFechaDesde = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filtros, fechaDesde: e.target.value || undefined });
  };

  const handleFechaHasta = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filtros, fechaHasta: e.target.value || undefined });
  };

  const handleLimpiar = () => {
    onChange({ estado: undefined, fechaDesde: undefined, fechaHasta: undefined });
  };

  return (
    <div className="flex flex-wrap gap-4 items-end bg-gray-50 p-4 rounded-lg border border-gray-200">
      {/* Selector de estado */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-700">Estado</label>
        <select
          value={filtros.estado ?? ''}
          onChange={handleEstado}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          {ESTADOS.map((e) => (
            <option key={e.value} value={e.value}>
              {e.label}
            </option>
          ))}
        </select>
      </div>

      {/* Fecha desde */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-700">Desde</label>
        <input
          type="date"
          value={filtros.fechaDesde ?? ''}
          onChange={handleFechaDesde}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* Fecha hasta */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-700">Hasta</label>
        <input
          type="date"
          value={filtros.fechaHasta ?? ''}
          onChange={handleFechaHasta}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* Limpiar */}
      <button
        onClick={handleLimpiar}
        className="px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-100"
      >
        Limpiar filtros
      </button>
    </div>
  );
};

export default PedidoFilters;
