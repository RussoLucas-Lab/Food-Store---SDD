/**
 * TopProductosBarChart — BarChart de productos más vendidos.
 *
 * Usa recharts BarChart.
 * Incluye filtro de fecha.
 * Consume useMetricasProductosTop.
 */

import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useMetricasProductosTop } from '../hooks/useMetricas';

const TopProductosBarChart: React.FC = () => {
  const [desde, setDesde] = useState<string>('');
  const [hasta, setHasta] = useState<string>('');
  const [top, setTop] = useState<number>(10);

  const { data, isLoading, isError } = useMetricasProductosTop({
    top,
    desde: desde || undefined,
    hasta: hasta || undefined,
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <h3 className="text-base font-semibold text-gray-700 flex-1">Productos más vendidos</h3>

        <label className="flex items-center gap-1 text-sm text-gray-600">
          Top:
          <select
            value={top}
            onChange={(e) => setTop(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
        </label>

        <label className="flex items-center gap-1 text-sm text-gray-600">
          Desde:
          <input
            type="date"
            value={desde}
            onChange={(e) => setDesde(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          />
        </label>

        <label className="flex items-center gap-1 text-sm text-gray-600">
          Hasta:
          <input
            type="date"
            value={hasta}
            onChange={(e) => setHasta(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          />
        </label>
      </div>

      {isLoading && (
        <div className="animate-pulse h-48 bg-gray-100 rounded" aria-label="Cargando gráfico..." />
      )}

      {isError && !isLoading && (
        <p className="text-red-500 text-sm py-8 text-center">
          Error al cargar productos top
        </p>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <ResponsiveContainer width="100%" height={240}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 20, left: 60, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tick={{ fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="nombre"
              tick={{ fontSize: 10 }}
              width={80}
            />
            <Tooltip
              formatter={(value: number) => [`${value} unidades`, 'Vendidos']}
            />
            <Bar dataKey="cantidad_vendida" fill="#10b981" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}

      {!isLoading && !isError && data?.length === 0 && (
        <p className="text-gray-400 text-sm py-8 text-center">
          No hay productos vendidos en el período seleccionado
        </p>
      )}
    </div>
  );
};

export default TopProductosBarChart;
