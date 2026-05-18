/**
 * StockPage — Gestión de stock del panel admin.
 *
 * Funcionalidades:
 * - Lista todos los productos (incluidos no disponibles)
 * - Muestra StockAlertList con umbral configurable (default 5)
 * - Permite actualizar stock vía PATCH /api/v1/productos/{id}/stock
 * - Accessible para ADMIN y STOCK
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@/shared/context/AuthContext';
import StockAlertList from '../components/StockAlertList';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

interface Producto {
  id: number;
  nombre: string;
  stock_disponible: number;
  disponible: boolean;
  base_price?: number;
}

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

/**
 * StockPage — admin page for stock management.
 */
const StockPage: React.FC = () => {
  const { token } = useAuth();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [umbral, setUmbral] = useState(5);
  const [editingStock, setEditingStock] = useState<Record<number, string>>({});
  const [updating, setUpdating] = useState<Record<number, boolean>>({});

  const loadProductos = async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${BASE_URL}/api/v1/productos`, {
        headers: authHeaders(token),
        params: { include_inactive: true, limit: 100 },
      });
      // Support both { items: [...] } and plain array responses
      const items: Producto[] = Array.isArray(res.data)
        ? res.data
        : (res.data.items ?? []);
      setProductos(items);
    } catch {
      setError('Error al cargar productos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProductos();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleUpdateStock = async (productoId: number) => {
    const nuevoStock = parseInt(editingStock[productoId] ?? '0', 10);
    if (isNaN(nuevoStock) || nuevoStock < 0 || !token) return;

    setUpdating((prev) => ({ ...prev, [productoId]: true }));
    try {
      await axios.patch(
        `${BASE_URL}/api/v1/productos/${productoId}/stock`,
        { stock: nuevoStock },
        { headers: authHeaders(token) }
      );
      // Actualizar localmente
      setProductos((prev) =>
        prev.map((p) => (p.id === productoId ? { ...p, stock_disponible: nuevoStock } : p))
      );
      setEditingStock((prev) => {
        const next = { ...prev };
        delete next[productoId];
        return next;
      });
    } catch {
      setError(`Error al actualizar stock del producto ${productoId}`);
    } finally {
      setUpdating((prev) => ({ ...prev, [productoId]: false }));
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Gestión de Stock</h1>

      {/* Umbral configurable */}
      <div className="flex items-center gap-3 mb-6">
        <label className="text-sm text-gray-700 font-medium">
          Umbral de alerta de stock bajo:
          <input
            type="number"
            min={0}
            max={100}
            value={umbral}
            onChange={(e) => setUmbral(Number(e.target.value))}
            className="ml-2 border rounded px-2 py-1 text-sm w-16"
            aria-label="Umbral de stock bajo"
          />
          &nbsp;unidades
        </label>
      </div>

      {/* Alertas de stock */}
      {productos.length > 0 && (
        <div className="mb-6">
          <StockAlertList productos={productos} umbral={umbral} />
        </div>
      )}

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {loading && <p className="text-gray-400 text-sm mb-4">Cargando productos...</p>}

      {/* Tabla de todos los productos */}
      {!loading && (
        <div className="overflow-x-auto rounded-lg shadow">
          <table className="w-full bg-white text-left text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">ID</th>
                <th className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">Nombre</th>
                <th className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">Stock actual</th>
                <th className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">Disponible</th>
                <th className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">Actualizar stock</th>
              </tr>
            </thead>
            <tbody>
              {productos.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-400">
                    No hay productos cargados
                  </td>
                </tr>
              ) : (
                productos.map((prod) => (
                  <tr
                    key={prod.id}
                    className={`border-b hover:bg-gray-50 ${
                      prod.stock_disponible === 0
                        ? 'bg-red-50'
                        : prod.stock_disponible <= umbral
                        ? 'bg-yellow-50'
                        : ''
                    }`}
                  >
                    <td className="px-4 py-2 text-gray-500">{prod.id}</td>
                    <td className="px-4 py-2 font-medium">{prod.nombre}</td>
                    <td
                      className={`px-4 py-2 font-semibold ${
                        prod.stock_disponible === 0
                          ? 'text-red-600'
                          : prod.stock_disponible <= umbral
                          ? 'text-yellow-700'
                          : 'text-gray-800'
                      }`}
                    >
                      {prod.stock_disponible}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                          prod.disponible
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {prod.disponible ? 'Sí' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          min={0}
                          value={editingStock[prod.id] ?? prod.stock_disponible}
                          onChange={(e) =>
                            setEditingStock((prev) => ({
                              ...prev,
                              [prod.id]: e.target.value,
                            }))
                          }
                          className="border rounded px-2 py-1 text-sm w-16"
                          aria-label={`Nuevo stock para ${prod.nombre}`}
                        />
                        <button
                          onClick={() => handleUpdateStock(prod.id)}
                          disabled={updating[prod.id]}
                          className="text-xs bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 disabled:opacity-50"
                          aria-label={`Actualizar stock de ${prod.nombre}`}
                        >
                          {updating[prod.id] ? '...' : 'Actualizar'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default StockPage;
