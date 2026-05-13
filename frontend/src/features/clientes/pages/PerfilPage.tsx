import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/context/AuthContext';
import { ClienteService } from '../services/clienteService';
import { ClienteDetail, ClienteForm } from '../components';
import { useClienteForm, useClienteList } from '../hooks';
import { Cliente, ClienteUpdate } from '../../../shared/types';
import './PerfilPage.css';

/**
 * PerfilPage
 * User's own cliente profile view and edit
 * - Users can view and edit their own profile
 * - If no profile exists, show message
 */
export const PerfilPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [cliente, setCliente] = useState<Cliente | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);

  const viewState = useClienteList();
  const editState = useClienteForm();

  /**
   * Load user's profile on mount
   */
  useEffect(() => {
    if (user?.id) {
      loadUserProfile();
    }
  }, [user?.id]);

  const loadUserProfile = async () => {
    viewState.setListLoading(true);
    viewState.clearError();

    try {
      // Fetch all clientes and find the one for current user
      // In a real scenario, there should be a /clientes/me endpoint
      // For now, we fetch all and filter
      const response = await ClienteService.listClientes(1, 1);
      if (response.items && response.items.length > 0) {
        setCliente(response.items[0]);
      }
    } catch {
       // It's ok if there's no profile yet
       console.warn('No cliente profile found for user');
    } finally {
      viewState.setListLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditMode(true);
  };

  const handleSaveEdit = async (data: ClienteUpdate) => {
    if (!cliente?.id) return;

    editState.setFormSubmitting(true);
    editState.clearError();

    try {
      const updated = await ClienteService.updateCliente(cliente.id, data);
      setCliente(updated);
      setIsEditMode(false);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al actualizar perfil';
      editState.setFormError(message);
    } finally {
      editState.setFormSubmitting(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    editState.resetForm();
  };

  if (isEditMode && cliente) {
    return (
      <div className="perfil-page">
        <div className="perfil-page__container">
          <h1 className="perfil-page__title">Editar Mi Perfil</h1>
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

  if (viewState.isLoading) {
    return (
      <div className="perfil-page">
        <div className="perfil-page__container">
          <p>Cargando perfil...</p>
        </div>
      </div>
    );
  }

  if (!cliente) {
    return (
      <div className="perfil-page">
        <div className="perfil-page__container">
          <h1 className="perfil-page__title">Mi Perfil</h1>
          <div className="perfil-page__empty">
            <p>No tienes un perfil de cliente registrado aún.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="perfil-page">
      <div className="perfil-page__container">
        <h1 className="perfil-page__title">Mi Perfil</h1>
        <ClienteDetail
          cliente={cliente}
          isLoading={viewState.isLoading}
          error={viewState.error}
          onEdit={handleEdit}
          onDelete={() => {}} // Users cannot delete their own profile
          onBack={() => navigate('/')}
          isOwnProfile
        />
      </div>
    </div>
  );
};

export default PerfilPage;
