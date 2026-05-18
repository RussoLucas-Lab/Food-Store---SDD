/**
 * PedidosEstadoPieChart — PieChart de distribución de pedidos por estado.
 *
 * Usa recharts PieChart.
 * Incluye filtro de fecha.
 * Consume useMetricasPedidosEstado.
 */

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useMetricasPedidosEstado } from '../hooks/useMetricas';

// Paleta de colores para los estados
const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: '#f59e0b',
  CONFIRMADO: '#3b82f6',
  EN_PREPARACION: '#8b5cf6',
  EN_CAMINO: '#6366f1',
  ENTREGADO: '#10b981',
  CANCELADO: '#ef4444',
};

const DEFAULT_COLOR = '#94a3b8';

const PedidosEstadoPieChart: React.FC = () => {
  const [desde, setDesde] = useState<string>('');
  const [hasta, setHasta] = useState<string>('');

  const { data, isLoading, isError } = useMetricasPedidosEstado({
    desde: desde || undefined,
    hasta: hasta || undefined,
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <h3 className="text-base font-semibold text-gray-700 flex-1">
          Pedidos por estado
        </h3>

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
        <div
          className="animate-pulse h-48 bg-gray-100 rounded"
          aria-label="Cargando gráfico..."
        />
      )}

      {isError && !isLoading && (
        <p className="text-red-500 text-sm py-8 text-center">
          Error al cargar distribución de pedidos
        </p>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={data}
              dataKey="cantidad"
              nameKey="estado"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ estado, percent }) =>
                `${estado} ${(percent * 100).toFixed(0)}%`
              }
              labelLine={false}
            >
              {data.map((entry) => (
                <Cell
                  key={entry.estado}
                  fill={ESTADO_COLORS[entry.estado] ?? DEFAULT_COLOR}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => [`${value} pedidos`, 'Cantidad']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}

      {!isLoading && !isError && data?.length === 0 && (
        <p className="text-gray-400 text-sm py-8 text-center">
          No hay pedidos en el período seleccionado
        </p>
      )}
    </div>
  );
};

export default PedidosEstadoPieChart;
