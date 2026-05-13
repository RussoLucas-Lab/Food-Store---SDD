import React from 'react';
import { Cliente } from '../../../../shared/types';
import { useAuth } from '../../../../shared/context/AuthContext';
import Button from '../../../../shared/components/atoms/Button';
import './ClienteDetail.css';

interface ClienteDetailProps {
  cliente: Cliente;
  isLoading: boolean;
  error: string | null;
  onEdit: () => void;
  onDelete: () => void;
  onBack: () => void;
  isOwnProfile?: boolean;
}

/**
 * ClienteDetail Component
 * Displays a single cliente with full details
 * - Shows all cliente information
 * - Provides edit/delete actions (admin only, or user editing own profile)
 * - Shows soft-delete status
 */
export const ClienteDetail: React.FC<ClienteDetailProps> = ({
  cliente,
  isLoading,
  error,
  onEdit,
  onDelete,
  onBack,
  isOwnProfile = false,
}) => {
  const { hasRole } = useAuth();
  const isAdmin = hasRole('ADMIN');
  const canEdit = isAdmin || isOwnProfile;

  if (isLoading) {
    return <div className="cliente-detail cliente-detail--loading">Cargando cliente...</div>;
  }

  if (error) {
    return <div className="cliente-detail cliente-detail--error">Error: {error}</div>;
  }

  return (
    <div className="cliente-detail">
      <div className="cliente-detail__header">
        <h1 className="cliente-detail__title">{cliente.nombre}</h1>
        <Button variant="secondary" onClick={onBack} className="cliente-detail__back">
          ← Volver
        </Button>
      </div>

      <div className="cliente-detail__content">
        <div className="cliente-detail__field-group">
          <div className="cliente-detail__field">
            <label className="cliente-detail__label">Email</label>
            <p className="cliente-detail__value">{cliente.email}</p>
          </div>

          <div className="cliente-detail__field">
            <label className="cliente-detail__label">Teléfono</label>
            <p className="cliente-detail__value">{cliente.telefono}</p>
          </div>

          <div className="cliente-detail__field">
            <label className="cliente-detail__label">Dirección</label>
            <p className="cliente-detail__value">{cliente.direccion}</p>
          </div>

          <div className="cliente-detail__field">
            <label className="cliente-detail__label">Estado</label>
            <p className="cliente-detail__value">
              <span
                className={`cliente-detail__status ${cliente.activo ? 'cliente-detail__status--active' : 'cliente-detail__status--inactive'}`}
              >
                {cliente.activo ? 'Activo' : 'Inactivo'}
              </span>
            </p>
          </div>

          <div className="cliente-detail__field">
            <label className="cliente-detail__label">Fecha de creación</label>
            <p className="cliente-detail__value">
              {new Date(cliente.created_at).toLocaleDateString('es-AR')}
            </p>
          </div>

          <div className="cliente-detail__field">
            <label className="cliente-detail__label">Última actualización</label>
            <p className="cliente-detail__value">
              {new Date(cliente.updated_at).toLocaleDateString('es-AR')}
            </p>
          </div>
        </div>
      </div>

      {canEdit && (
        <div className="cliente-detail__actions">
          <Button onClick={onEdit} className="cliente-detail__action-btn">
            Editar
          </Button>
          {isAdmin && (
            <Button
              variant="danger"
              onClick={() => {
                if (
                  confirm(`¿Seguro que deseas eliminar a ${cliente.nombre}? Esta acción no se puede deshacer.`)
                ) {
                  onDelete();
                }
              }}
              className="cliente-detail__action-btn"
            >
              Eliminar
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default ClienteDetail;
