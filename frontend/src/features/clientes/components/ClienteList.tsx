import React from 'react';
import { Cliente } from '../../../shared/types';
import { useAuth } from '../../../shared/context/AuthContext';
import { Button } from '../../../shared/components/atoms';
import './ClienteList.css';

interface ClienteListProps {
  clientes: Cliente[];
  isLoading: boolean;
  error: string | null;
  onDelete: (id: string) => void;
  onEdit: (cliente: Cliente) => void;
  onView: (id: string) => void;
}

/**
 * ClienteList Component
 * Displays a list of clientes in a table/card layout
 * - Shows active clientes only
 * - Supports role-based visibility (ADMIN sees all, USER sees limited)
 * - Provides actions: View, Edit, Delete
 */
export const ClienteList: React.FC<ClienteListProps> = ({
  clientes,
  isLoading,
  error,
  onDelete,
  onEdit,
  onView,
}) => {
  const { hasRole } = useAuth();
  const isAdmin = hasRole('ADMIN');

  if (isLoading) {
    return <div className="cliente-list cliente-list--loading">Cargando clientes...</div>;
  }

  if (error) {
    return <div className="cliente-list cliente-list--error">Error: {error}</div>;
  }

  if (clientes.length === 0) {
    return <div className="cliente-list cliente-list--empty">No hay clientes para mostrar</div>;
  }

  return (
    <div className="cliente-list">
      <div className="cliente-list__container">
        <table className="cliente-list__table">
          <thead className="cliente-list__head">
            <tr>
              <th>Nombre</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th>Dirección</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody className="cliente-list__body">
            {clientes.map((cliente) => (
              <tr key={cliente.id} className="cliente-list__row">
                <td className="cliente-list__cell">{cliente.nombre}</td>
                <td className="cliente-list__cell">{cliente.email}</td>
                <td className="cliente-list__cell">{cliente.telefono}</td>
                <td className="cliente-list__cell cliente-list__cell--truncate">
                  {cliente.direccion}
                </td>
                <td className="cliente-list__cell">
                  <span className={`cliente-list__status ${cliente.activo ? 'cliente-list__status--active' : 'cliente-list__status--inactive'}`}>
                    {cliente.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="cliente-list__cell cliente-list__actions">
                  <Button
                    variant="secondary"
                    size="small"
                    onClick={() => onView(cliente.id)}
                    className="cliente-list__action-btn"
                  >
                    Ver
                  </Button>

                  {isAdmin && (
                    <>
                      <Button
                        variant="secondary"
                        size="small"
                        onClick={() => onEdit(cliente)}
                        className="cliente-list__action-btn"
                      >
                        Editar
                      </Button>
                      <Button
                        variant="danger"
                        size="small"
                        onClick={() => {
                          if (confirm(`¿Seguro que deseas eliminar a ${cliente.nombre}?`)) {
                            onDelete(cliente.id);
                          }
                        }}
                        className="cliente-list__action-btn"
                      >
                        Eliminar
                      </Button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ClienteList;
