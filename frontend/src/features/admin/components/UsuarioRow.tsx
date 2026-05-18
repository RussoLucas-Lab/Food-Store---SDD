/**
 * UsuarioRow — Fila de usuario en la tabla de gestión.
 *
 * Muestra:
 * - Datos del usuario (nombre, email, estado)
 * - UsuarioRolEditor para cambiar el rol
 * - Toggle de activar/desactivar cuenta
 * - Errores de mutación sin afectar el listado
 */

import React, { useState } from 'react';
import UsuarioRolEditor from './UsuarioRolEditor';
import { useUpdateUsuario, useToggleUsuarioActivo } from '../hooks/useUsuarios';
import type { UsuarioAdmin } from '../services/adminUsuariosApi';

interface UsuarioRowProps {
  usuario: UsuarioAdmin;
  currentUserId: number;
}

/**
 * UsuarioRow displays one user and allows editing role and toggling active status.
 */
const UsuarioRow: React.FC<UsuarioRowProps> = ({ usuario, currentUserId }) => {
  const [mutationError, setMutationError] = useState<string | null>(null);

  const updateMutation = useUpdateUsuario();
  const toggleMutation = useToggleUsuarioActivo();

  const handleRolChange = (newRole: string) => {
    setMutationError(null);
    updateMutation.mutate(
      { userId: usuario.id, payload: { role: newRole } },
      {
        onError: (err: unknown) => {
          const message =
            err instanceof Error ? err.message : 'Error al cambiar el rol';
          setMutationError(message);
        },
      }
    );
  };

  const handleToggleActivo = () => {
    setMutationError(null);
    toggleMutation.mutate(
      { userId: usuario.id, activo: !usuario.is_active },
      {
        onError: (err: unknown) => {
          const message =
            err instanceof Error ? err.message : 'Error al cambiar el estado';
          setMutationError(message);
        },
      }
    );
  };

  const isSelf = usuario.id === currentUserId;

  return (
    <tr className="border-b hover:bg-gray-50">
      <td className="px-4 py-3 text-sm text-gray-900">
        {usuario.nombre ?? '—'}
      </td>
      <td className="px-4 py-3 text-sm text-gray-600">{usuario.email}</td>
      <td className="px-4 py-3 text-sm">
        <UsuarioRolEditor
          currentRole={usuario.role}
          onSave={handleRolChange}
          isLoading={updateMutation.isPending}
          disabled={isSelf}
        />
      </td>
      <td className="px-4 py-3 text-sm">
        <span
          className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
            usuario.is_active
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {usuario.is_active ? 'Activo' : 'Inactivo'}
        </span>
      </td>
      <td className="px-4 py-3 text-sm">
        <button
          onClick={handleToggleActivo}
          disabled={toggleMutation.isPending || isSelf}
          className={`text-xs px-3 py-1 rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
            usuario.is_active
              ? 'bg-red-100 text-red-700 hover:bg-red-200'
              : 'bg-green-100 text-green-700 hover:bg-green-200'
          }`}
          aria-label={
            usuario.is_active
              ? `Desactivar cuenta de ${usuario.email}`
              : `Activar cuenta de ${usuario.email}`
          }
        >
          {toggleMutation.isPending
            ? '...'
            : usuario.is_active
            ? 'Desactivar'
            : 'Activar'}
        </button>
        {isSelf && (
          <span className="text-xs text-gray-400 ml-2">(tu cuenta)</span>
        )}
      </td>
      <td className="px-4 py-3 text-xs text-red-500">
        {mutationError}
      </td>
    </tr>
  );
};

export default UsuarioRow;
