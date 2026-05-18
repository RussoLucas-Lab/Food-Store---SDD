/**
 * VentasLineChart — Gráfico de líneas para serie temporal de ventas.
 *
 * Usa recharts LineChart.
 * Incluye selector de rango de fechas y granularidad.
 * Consume useMetricasVentas.
 */

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useMetricasVentas } from '../hooks/useMetricas';
import type { Granularidad } from '../services/adminMetricasApi';

const VentasLineChart: React.FC = () => {
  const [desde, setDesde] = useState<string>('');
  const [hasta, setHasta] = useState<string>('');
  const [granularidad, setGranularidad] = useState<Granularidad>('dia');

  const { data, isLoading, isError } = useMetricasVentas({
    desde: desde || undefined,
    hasta: hasta || undefined,
    granularidad,
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <h3 className="text-base font-semibold text-gray-700 flex-1">Ventas por período</h3>

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

        <label className="flex items-center gap-1 text-sm text-gray-600">
          Granularidad:
          <select
            value={granularidad}
            onChange={(e) => setGranularidad(e.target.value as Granularidad)}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="dia">Día</option>
            <option value="semana">Semana</option>
            <option value="mes">Mes</option>
          </select>
        </label>
      </div>

      {isLoading && (
        <div className="animate-pulse h-48 bg-gray-100 rounded" aria-label="Cargando gráfico..." />
      )}

      {isError && !isLoading && (
        <p className="text-red-500 text-sm py-8 text-center">Error al cargar ventas</p>
      )}

      {!isLoading && !isError && data && (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="periodo" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value: number) => [`$${value.toLocaleString('es-AR')}`, 'Ventas']}
            />
            <Line
              type="monotone"
              dataKey="monto"
              stroke="#4f46e5"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}

      {!isLoading && !isError && data?.length === 0 && (
        <p className="text-gray-400 text-sm py-8 text-center">
          No hay ventas en el período seleccionado
        </p>
      )}
    </div>
  );
};

export default VentasLineChart;
