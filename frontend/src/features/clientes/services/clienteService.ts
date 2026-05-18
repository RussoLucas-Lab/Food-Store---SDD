import { httpClient, handleApiError, withRetry } from '../../../shared/services/httpClient';
import {
  ClienteCreate,
  ClienteUpdate,
  ClienteResponse,
  ClienteListResponse,
} from '../../../shared/types';

const API_ENDPOINT = '/api/v1/clientes';

/**
 * ClienteService
 * Handles all HTTP requests to the /clientes API endpoints
 * Implements error handling, retry logic, and token refresh
 */
export class ClienteService {
  /**
   * Create a new cliente
   * POST /clientes
   * Requires: ADMIN role
   */
  static async createCliente(data: ClienteCreate): Promise<ClienteResponse> {
    try {
      return await withRetry(async () => {
        const response = await httpClient.post<ClienteResponse>(API_ENDPOINT, data);
        return response.data;
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * Get all active clientes
   * GET /clientes
   * Admin: returns all active clientes
   * User: returns only their own profile
   */
  static async listClientes(
    page: number = 1,
    limit: number = 10
  ): Promise<ClienteListResponse> {
    try {
      return await withRetry(async () => {
        const response = await httpClient.get<ClienteListResponse>(API_ENDPOINT, {
          params: { page, limit },
        });
        return response.data;
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * Get a specific cliente by ID
   * GET /clientes/{id}
   * Admin: can view any cliente
   * User: can only view their own profile
   */
  static async getCliente(id: string): Promise<ClienteResponse> {
    try {
      return await withRetry(async () => {
        const response = await httpClient.get<ClienteResponse>(`${API_ENDPOINT}/${id}`);
        return response.data;
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * Update a cliente
   * PATCH /clientes/{id}
   * Admin: can update any cliente
   * User: can only update their own profile
   */
  static async updateCliente(id: string, data: ClienteUpdate): Promise<ClienteResponse> {
    try {
      return await withRetry(async () => {
        const response = await httpClient.patch<ClienteResponse>(
          `${API_ENDPOINT}/${id}`,
          data
        );
        return response.data;
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * Soft-delete a cliente
   * DELETE /clientes/{id}
   * Requires: ADMIN role
   * Marks cliente as inactive (activo=false)
   */
  static async deleteCliente(id: string): Promise<void> {
    try {
      await withRetry(async () => {
        await httpClient.delete(`${API_ENDPOINT}/${id}`);
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * Reactivate a soft-deleted cliente
   * PATCH /clientes/{id}/reactivar
   * Requires: ADMIN role
   */
  static async reactivateCliente(id: string): Promise<ClienteResponse> {
    try {
      return await withRetry(async () => {
        const response = await httpClient.patch<ClienteResponse>(
          `${API_ENDPOINT}/${id}/reactivar`
        );
        return response.data;
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * Search clientes by name or email
   * GET /clientes/search?q=...
   * Requires: ADMIN role
   */
  static async searchClientes(query: string): Promise<ClienteResponse[]> {
    try {
      return await withRetry(async () => {
        const response = await httpClient.get<ClienteResponse[]>(`${API_ENDPOINT}/search`, {
          params: { q: query },
        });
        return response.data;
      });
    } catch (error) {
      throw handleApiError(error);
    }
  }
}

export default ClienteService;
