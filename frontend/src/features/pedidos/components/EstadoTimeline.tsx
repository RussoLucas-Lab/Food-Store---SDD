/**
 * EstadoTimeline — Renderiza la línea de tiempo de estados de un pedido
 * a partir del historial (array de HistorialEstadoPedidoResponse).
 */

import React from 'react';
import type { HistorialEstadoPedidoResponse } from '../services/pedidoClient';
import EstadoBadge from './EstadoBadge';

interface EstadoTimelineProps {
  historial: HistorialEstadoPedidoResponse[];
}

function formatFecha(iso: string): string {
  try {
    return new Date(iso).toLocaleString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

const EstadoTimeline: React.FC<EstadoTimelineProps> = ({ historial }) => {
  if (!historial || historial.length === 0) {
    return <p className="text-gray-500 text-sm">Sin historial de estados.</p>;
  }

  return (
    <ol className="relative border-l border-gray-200 ml-3">
      {historial.map((entry, idx) => (
        <li key={entry.id ?? idx} className="mb-6 ml-6">
          {/* Círculo del timeline */}
          <span className="absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full bg-white border-2 border-blue-400">
            <span className="h-2.5 w-2.5 rounded-full bg-blue-400" />
          </span>

          <div className="flex flex-col gap-1">
            <EstadoBadge estado={entry.estado_nuevo} />
            <time className="text-xs text-gray-500">{formatFecha(entry.timestamp)}</time>
            {entry.observacion && (
              <p className="text-sm text-gray-600 italic">{entry.observacion}</p>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
};

export default EstadoTimeline;
