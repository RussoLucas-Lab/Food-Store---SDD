/**
 * StockAlertList — Lista de productos con stock bajo el umbral configurado.
 *
 * Props:
 * - productos: lista de productos con su stock
 * - umbral: nivel mínimo de stock para generar alerta (default 5)
 *
 * Recalcula las alertas cada vez que cambia el umbral o la lista de productos.
 */

import React from 'react';

interface Producto {
  id: number;
  nombre: string;
  stock_disponible: number;
  disponible?: boolean;
}

interface StockAlertListProps {
  productos: Producto[];
  umbral?: number;
}

/**
 * StockAlertList highlights products below the stock threshold.
 */
const StockAlertList: React.FC<StockAlertListProps> = ({
  productos,
  umbral = 5,
}) => {
  const alertas = productos.filter((p) => p.stock_disponible <= umbral);

  if (alertas.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700">
        Todos los productos tienen stock suficiente (umbral: {umbral} unidades).
      </div>
    );
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <h4 className="text-sm font-semibold text-yellow-800 mb-2">
        Alertas de stock bajo ({alertas.length} productos)
        <span className="ml-2 text-xs font-normal text-yellow-600">
          umbral: ≤{umbral} unidades
        </span>
      </h4>
      <ul className="space-y-1">
        {alertas.map((p) => (
          <li key={p.id} className="flex justify-between text-sm">
            <span className="text-gray-800">{p.nombre}</span>
            <span
              className={`font-semibold ${
                p.stock_disponible === 0 ? 'text-red-600' : 'text-yellow-700'
              }`}
              aria-label={`Stock: ${p.stock_disponible}`}
            >
              {p.stock_disponible === 0 ? 'SIN STOCK' : `${p.stock_disponible} unid.`}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StockAlertList;
