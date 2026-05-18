/**
 * DashboardPage — Panel principal de métricas del admin.
 *
 * Compone:
 * - KpiCards con useMetricasResumen (carga independiente)
 * - VentasLineChart
 * - TopProductosBarChart
 * - PedidosEstadoPieChart
 *
 * Cada gráfico tiene su propio estado de carga y error independientes.
 */

import React from 'react';
import KpiCard from '../components/KpiCard';
import VentasLineChart from '../components/VentasLineChart';
import TopProductosBarChart from '../components/TopProductosBarChart';
import PedidosEstadoPieChart from '../components/PedidosEstadoPieChart';
import { useMetricasResumen } from '../hooks/useMetricas';

/**
 * DashboardPage displays business KPIs and charts.
 */
const DashboardPage: React.FC = () => {
  const resumen = useMetricasResumen();

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {/* KPI Cards — datos del endpoint de resumen */}
      <section aria-label="KPIs del negocio" className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KpiCard
          title="Ventas totales"
          value={resumen.data?.ventas_totales ?? 0}
          prefix="$"
          isLoading={resumen.isLoading}
          isError={resumen.isError}
          description="Pedidos en estado efectivo"
        />
        <KpiCard
          title="Pedidos efectivos"
          value={resumen.data?.cantidad_pedidos ?? 0}
          isLoading={resumen.isLoading}
          isError={resumen.isError}
          description="Confirmados, en prep., en camino o entregados"
        />
        <KpiCard
          title="Usuarios registrados"
          value={resumen.data?.cantidad_usuarios ?? 0}
          isLoading={resumen.isLoading}
          isError={resumen.isError}
        />
        <KpiCard
          title="Productos sin stock"
          value={resumen.data?.productos_sin_stock ?? 0}
          isLoading={resumen.isLoading}
          isError={resumen.isError}
          description="Stock = 0"
        />
      </section>

      {/* Gráficos — cada uno carga de forma independiente */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="lg:col-span-2">
          <VentasLineChart />
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopProductosBarChart />
        <PedidosEstadoPieChart />
      </section>
    </div>
  );
};

export default DashboardPage;
