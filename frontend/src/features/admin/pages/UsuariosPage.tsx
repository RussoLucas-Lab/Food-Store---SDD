/**
 * UsuariosPage — Gestión de usuarios del panel admin.
 *
 * Funcionalidades:
 * - Búsqueda por nombre/email
 * - Filtros por rol y estado activo
 * - Paginación
 * - Tabla con UsuarioRow (edición de rol + toggle activo)
 * - Errores de mutación se muestran en la fila correspondiente sin afectar el listado
 */

import React, { useState } from 'react';
import { useUsuarios } from '../hooks/useUsuarios';
import { useAuth } from '@/shared/context/AuthContext';
import UsuarioRow from '../components/UsuarioRow';

const ROLES_FILTER = ['', 'ADMIN', 'CLIENT', 'STOCK', 'PEDIDOS'];

/**
 * UsuariosPage — admin page for user management.
 */
const UsuariosPage: React.FC = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [rol, setRol] = useState('');
  const [activo, setActivo] = useState<string>('');
  const PAGE_SIZE = 20;

  const activoFilter =
    activo === 'true' ? true : activo === 'false' ? false : undefined;

  const { data, isLoading, isError } = useUsuarios({
    page,
    size: PAGE_SIZE,
    q: q || undefined,
    rol: rol || undefined,
    activo: activoFilter,
  });

  const currentUserId =
    user?.id !== undefined ? Number(user.id) : -1;

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Gestión de Usuarios</h1>

      {/* Filtros */}
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Buscar por nombre o email..."
          value={q}
          onChange={(e) => { setQ(e.target.value); setPage(1); }}
          className="border rounded px-3 py-2 text-sm flex-1 min-w-48"
          aria-label="Buscar usuario"
        />

        <select
          value={rol}
          onChange={(e) => { setRol(e.target.value); setPage(1); }}
          className="border rounded px-3 py-2 text-sm"
          aria-label="Filtrar por rol"
        >
          {ROLES_FILTER.map((r) => (
            <option key={r} value={r}>
              {r === '' ? 'Todos los roles' : r}
            </option>
          ))}
        </select>

        <select
          value={activo}
          onChange={(e) => { setActivo(e.target.value); setPage(1); }}
          className="border rounded px-3 py-2 text-sm"
          aria-label="Filtrar por estado"
        >
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>

      {/* Estado de carga / error */}
      {isLoading && (
        <div className="py-8 text-center text-gray-500">Cargando usuarios...</div>
      )}

      {isError && !isLoading && (
        <div className="py-8 text-center text-red-500">
          Error al cargar los usuarios. Intente nuevamente.
        </div>
      )}

      {/* Tabla */}
      {!isLoading && !isError && data && (
        <>
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full bg-white text-left">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Nombre</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Email</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Rol</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Estado</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Acciones</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Error</th>
                </tr>
              </thead>
              <tbody>
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                      No se encontraron usuarios
                    </td>
                  </tr>
                ) : (
                  data.items.map((usuario) => (
                    <UsuarioRow
                      key={usuario.id}
                      usuario={usuario}
                      currentUserId={currentUserId}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
          <div className="flex justify-between items-center mt-4">
            <p className="text-sm text-gray-500">
              {data.total} usuarios — Página {data.page} de {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default UsuariosPage;
