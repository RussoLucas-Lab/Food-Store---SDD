/**
 * KpiCard — Componente para mostrar un KPI individual en el dashboard.
 *
 * Props:
 * - title: etiqueta del KPI
 * - value: valor a mostrar (número o string)
 * - description: descripción opcional
 * - isLoading: estado de carga
 * - isError: estado de error
 */

import React from 'react';

interface KpiCardProps {
  title: string;
  value: number | string;
  description?: string;
  isLoading?: boolean;
  isError?: boolean;
  prefix?: string;
  suffix?: string;
}

/**
 * KpiCard displays a single business KPI metric.
 */
const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  description,
  isLoading = false,
  isError = false,
  prefix = '',
  suffix = '',
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-6 flex flex-col gap-2">
      <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">{title}</p>

      {isLoading && (
        <div className="animate-pulse h-8 bg-gray-200 rounded w-24" aria-label="Cargando..." />
      )}

      {isError && !isLoading && (
        <p className="text-red-500 text-sm">Error al cargar</p>
      )}

      {!isLoading && !isError && (
        <p className="text-3xl font-bold text-gray-900">
          {prefix}
          {typeof value === 'number' ? value.toLocaleString('es-AR') : value}
          {suffix}
        </p>
      )}

      {description && !isLoading && !isError && (
        <p className="text-xs text-gray-400">{description}</p>
      )}
    </div>
  );
};

export default KpiCard;
