/**
 * DirectionSelector — Selector de dirección de entrega.
 *
 * Carga las direcciones del cliente desde la API (TanStack Query) y permite
 * seleccionar una. Expone la selección vía callback onSelect.
 *
 * Estado de servidor: TanStack Query (no Zustand).
 */

import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getDirecciones, type DireccionEntregaResponse } from '../services/direccionClient';

interface DirectionSelectorProps {
  /** Dirección actualmente seleccionada */
  selectedId: number | null;
  /** Callback invocado cuando el usuario selecciona una dirección */
  onSelect: (direccionId: number | null) => void;
}

const DirectionSelector: React.FC<DirectionSelectorProps> = ({ selectedId, onSelect }) => {
  const {
    data: direcciones = [],
    isLoading,
    isError,
  } = useQuery<DireccionEntregaResponse[]>({
    queryKey: ['direcciones'],
    queryFn: getDirecciones,
    staleTime: 1000 * 60 * 5, // 5 min
  });

  // Pre-seleccionar la dirección predeterminada cuando carga la lista
  useEffect(() => {
    if (direcciones.length > 0 && selectedId === null) {
      const predeterminada = direcciones.find((d) => d.es_predeterminada);
      const primera = direcciones[0];
      onSelect((predeterminada ?? primera).id);
    }
  }, [direcciones, selectedId, onSelect]);

  if (isLoading) {
    return <p className="text-sm text-gray-500">Cargando direcciones...</p>;
  }

  if (isError) {
    return <p className="text-sm text-red-500">No se pudieron cargar las direcciones.</p>;
  }

  if (direcciones.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        <p>No tenés direcciones guardadas.</p>
        <a href="/perfil" className="text-blue-600 hover:underline text-sm">
          + Agregar Nueva Dirección
        </a>
      </div>
    );
  }

  return (
    <div data-testid="direction-selector">
      <h4 className="font-medium text-gray-900 mb-2">Dirección de entrega</h4>
      <ul className="space-y-2">
        {direcciones.map((dir) => (
          <li key={dir.id}>
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="radio"
                name="direccion"
                value={dir.id}
                checked={selectedId === dir.id}
                onChange={() => onSelect(dir.id)}
                className="mt-1"
              />
              <div>
                <p className="font-medium text-gray-900">
                  {dir.calle} {dir.numero}
                  {dir.piso ? `, Piso ${dir.piso}` : ''}
                  {dir.departamento ? ` Dpto. ${dir.departamento}` : ''}
                </p>
                <p className="text-sm text-gray-600">
                  {dir.ciudad}, {dir.provincia} ({dir.codigo_postal})
                </p>
                {dir.referencia && (
                  <p className="text-xs text-gray-500">{dir.referencia}</p>
                )}
                {dir.es_predeterminada && (
                  <span className="text-xs text-green-600 font-medium">Predeterminada</span>
                )}
              </div>
            </label>
          </li>
        ))}
      </ul>

      <a href="/perfil" className="text-blue-600 hover:underline text-sm mt-3 inline-block">
        + Agregar Nueva Dirección
      </a>
    </div>
  );
};

export default DirectionSelector;
