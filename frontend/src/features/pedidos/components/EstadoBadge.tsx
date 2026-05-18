/**
 * EstadoBadge — Muestra el estado de un pedido con estilo visual según el estado.
 */

import React from 'react';

interface EstadoBadgeProps {
  estado: string;
  className?: string;
}

const ESTADO_CONFIG: Record<string, { label: string; className: string }> = {
  PENDIENTE:      { label: 'Pendiente',       className: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
  CONFIRMADO:     { label: 'Confirmado',      className: 'bg-blue-100 text-blue-800 border-blue-300' },
  EN_PREPARACION: { label: 'En preparación',  className: 'bg-indigo-100 text-indigo-800 border-indigo-300' },
  EN_CAMINO:      { label: 'En camino',       className: 'bg-purple-100 text-purple-800 border-purple-300' },
  ENTREGADO:      { label: 'Entregado',       className: 'bg-green-100 text-green-800 border-green-300' },
  CANCELADO:      { label: 'Cancelado',       className: 'bg-red-100 text-red-800 border-red-300' },
};

const EstadoBadge: React.FC<EstadoBadgeProps> = ({ estado, className = '' }) => {
  const config = ESTADO_CONFIG[estado] ?? { label: estado, className: 'bg-gray-100 text-gray-800 border-gray-300' };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className} ${className}`}
    >
      {config.label}
    </span>
  );
};

export default EstadoBadge;
