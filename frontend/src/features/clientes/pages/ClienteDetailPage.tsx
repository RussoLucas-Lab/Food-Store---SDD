import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ClienteService } from '../services/clienteService';
import { ClienteDetail, ClienteForm } from '../components';
import { useClienteForm, useClienteList } from '../hooks';
import { Cliente, ClienteUpdate } from '../../../shared/types';
import './ClienteDetailPage.css';

/**
 * ClienteDetailPage
 * Display and edit a single cliente
 * - View mode: shows all details
 * - Edit mode: shows form for updating
 * - Can edit own profile (USER) or any profile (ADMIN)
 */
export const ClienteDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState<Cliente | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);

  const viewState = useClienteList();
  const editState = useClienteForm();

  if (!id) {
    return (
      <div className="cliente-detail-page">
        <div className="cliente-detail-page__error">Error: ID de cliente no válido</div>
      </div>
    );
  }

  /**
   * Load cliente on mount
   */
  useEffect(() => {
    loadCliente();
  }, [id]);

  const loadCliente = async () => {
    viewState.setListLoading(true);
    viewState.clearError();

    try {
      const data = await ClienteService.getCliente(id);
      setCliente(data);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al cargar cliente';
      viewState.setListError(message);
    } finally {
      viewState.setListLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditMode(true);
  };

  const handleSaveEdit = async (data: ClienteUpdate) => {
    editState.setFormSubmitting(true);
    editState.clearError();

    try {
      const updated = await ClienteService.updateCliente(id, data);
      setCliente(updated);
      setIsEditMode(false);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al actualizar cliente';
      editState.setFormError(message);
    } finally {
      editState.setFormSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      await ClienteService.deleteCliente(id);
      navigate('/clientes');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al eliminar cliente';
      viewState.setListError(message);
    }
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    editState.resetForm();
  };

  const handleBack = () => {
    navigate('/clientes');
  };

  if (isEditMode && cliente) {
    return (
      <div className="cliente-detail-page">
        <div className="cliente-detail-page__container">
          <h1 className="cliente-detail-page__title">Editar Cliente</h1>
          <ClienteForm
            cliente={cliente}
            isLoading={editState.isLoading}
            isSubmitting={editState.isSubmitting}
            error={editState.error}
            onSubmit={handleSaveEdit}
            onCancel={handleCancelEdit}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="cliente-detail-page">
      <div className="cliente-detail-page__container">
        {cliente && (
          <ClienteDetail
            cliente={cliente}
            isLoading={viewState.isLoading}
            error={viewState.error}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onBack={handleBack}
          />
        )}
      </div>
    </div>
  );
};

export default ClienteDetailPage;
