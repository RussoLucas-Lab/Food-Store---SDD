/**
 * UsuarioRolEditor — Editor del rol de un usuario.
 *
 * Props:
 * - currentRole: rol actual del usuario
 * - onSave: callback con el nuevo rol seleccionado
 * - isLoading: si hay una mutación en curso
 * - disabled: deshabilitar el editor
 */

import React, { useState } from 'react';

const ROLES_DISPONIBLES = ['ADMIN', 'CLIENT', 'STOCK', 'PEDIDOS'];

interface UsuarioRolEditorProps {
  currentRole: string;
  onSave: (newRole: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

/**
 * UsuarioRolEditor allows changing the role of a user.
 */
const UsuarioRolEditor: React.FC<UsuarioRolEditorProps> = ({
  currentRole,
  onSave,
  isLoading = false,
  disabled = false,
}) => {
  const [editing, setEditing] = useState(false);
  const [selectedRole, setSelectedRole] = useState(currentRole.toUpperCase());

  const handleSave = () => {
    if (selectedRole !== currentRole.toUpperCase()) {
      onSave(selectedRole);
    }
    setEditing(false);
  };

  const handleCancel = () => {
    setSelectedRole(currentRole.toUpperCase());
    setEditing(false);
  };

  if (!editing) {
    return (
      <span className="flex items-center gap-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
          {currentRole.toUpperCase()}
        </span>
        {!disabled && (
          <button
            onClick={() => setEditing(true)}
            className="text-xs text-blue-600 hover:underline"
            aria-label={`Editar rol de usuario`}
          >
            Editar
          </button>
        )}
      </span>
    );
  }

  return (
    <span className="flex items-center gap-2">
      <select
        value={selectedRole}
        onChange={(e) => setSelectedRole(e.target.value)}
        className="border rounded px-2 py-1 text-xs"
        disabled={isLoading}
        aria-label="Seleccionar rol"
      >
        {ROLES_DISPONIBLES.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>
      <button
        onClick={handleSave}
        disabled={isLoading}
        className="text-xs bg-indigo-600 text-white px-2 py-1 rounded hover:bg-indigo-700 disabled:opacity-50"
        aria-label="Guardar rol"
      >
        {isLoading ? '...' : 'Guardar'}
      </button>
      <button
        onClick={handleCancel}
        disabled={isLoading}
        className="text-xs text-gray-500 hover:underline"
        aria-label="Cancelar edición"
      >
        Cancelar
      </button>
    </span>
  );
};

export default UsuarioRolEditor;
