import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ClienteService } from '../services/clienteService';
import { ClienteForm } from '../components';
import { useClienteForm } from '../hooks';
import { ClienteCreate } from '../../../shared/types';
import './ClienteCreatePage.css';

/**
 * ClienteCreatePage
 * Form to create a new cliente
 * - Admin-only feature
 */
export const ClienteCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const formState = useClienteForm();

  const handleSubmit = async (data: ClienteCreate) => {
    formState.setFormSubmitting(true);
    formState.clearError();

    try {
      await ClienteService.createCliente(data);
      // Navigate to list on success
      navigate('/clientes');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al crear cliente';
      formState.setFormError(message);
    } finally {
      formState.setFormSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate('/clientes');
  };

  return (
    <div className="cliente-create-page">
      <div className="cliente-create-page__container">
        <h1 className="cliente-create-page__title">Crear Nuevo Cliente</h1>
        <ClienteForm
          isLoading={formState.isLoading}
          isSubmitting={formState.isSubmitting}
          error={formState.error}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default ClienteCreatePage;
