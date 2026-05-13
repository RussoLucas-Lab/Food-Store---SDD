import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/context/AuthContext';
import { ClienteService } from '../services/clienteService';
import { ClienteList, ClienteSearch } from '../components';
import { Button } from '../../../shared/components/atoms';
import { useClienteList } from '../hooks';
import { Cliente } from '../../../shared/types';
import './ClientesPage.css';

/**
 * ClientesPage
 * List all clientes with search functionality
 * - Admin: sees all active clientes
 * - User: sees only their own profile
 * - Search: admin-only feature
 */
export const ClientesPage: React.FC = () => {
   const navigate = useNavigate();
   const { hasRole } = useAuth();
   const isAdmin = hasRole('ADMIN');

   const listState = useClienteList();
   const [searchQuery, setSearchQuery] = useState('');

  /**
   * Load clientes on mount or when search changes
   */
  useEffect(() => {
    loadClientes();
  }, [searchQuery]);

  const loadClientes = async () => {
    listState.setListLoading(true);
    listState.clearError();

    try {
      let response;

      if (searchQuery && isAdmin) {
         // Search mode
         const results = await ClienteService.searchClientes(searchQuery);
         response = {
           items: results,
           total: results.length,
           page: 1,
           limit: results.length,
         };
       } else {
         // List all
         response = await ClienteService.listClientes(1, 50);
      }

      listState.setListItems(response.items);
      listState.setListPagination(response.page, response.limit, response.total);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al cargar clientes';
      listState.setListError(message);
    } finally {
      listState.setListLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleDelete = async (id: string) => {
    try {
      await ClienteService.deleteCliente(id);
      // Reload list
      await loadClientes();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al eliminar cliente';
      listState.setListError(message);
    }
  };

  const handleEdit = (cliente: Cliente) => {
    navigate(`/clientes/${cliente.id}/editar`);
  };

  const handleView = (id: string) => {
    navigate(`/clientes/${id}`);
  };

  const handleCreateNew = () => {
    navigate('/clientes/crear');
  };

  return (
    <div className="clientes-page">
      <div className="clientes-page__header">
        <h1 className="clientes-page__title">Gestión de Clientes</h1>
        {isAdmin && (
          <Button onClick={handleCreateNew} className="clientes-page__create-btn">
            + Nuevo Cliente
          </Button>
        )}
      </div>

      {isAdmin && <ClienteSearch onSearch={handleSearch} isLoading={listState.isLoading} />}

      <ClienteList
        clientes={listState.items}
        isLoading={listState.isLoading}
        error={listState.error}
        onDelete={handleDelete}
        onEdit={handleEdit}
        onView={handleView}
      />

      {!isAdmin && listState.items.length === 0 && !listState.isLoading && (
        <div className="clientes-page__info">
          <p>No tienes un perfil de cliente registrado aún.</p>
        </div>
      )}
    </div>
  );
};

export default ClientesPage;
