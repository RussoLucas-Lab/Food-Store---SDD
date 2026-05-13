/**
 * Shared types across the application
 */

export type UserRole = 'ADMIN' | 'USER' | 'GUEST';

/**
 * Cliente domain type
 * Represents a customer in the Food Store system
 */
export interface Cliente {
  id: string;
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
  user_id?: string | null;
}

/**
 * DTOs for Cliente API operations
 */
export interface ClienteCreate {
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  user_id?: string | null;
}

export interface ClienteUpdate {
  nombre?: string;
  email?: string;
  telefono?: string;
  direccion?: string;
}

export interface ClienteResponse {
  id: string;
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
  user_id?: string | null;
}

export interface ClienteListResponse {
  items: ClienteResponse[];
  total: number;
  page: number;
  limit: number;
}

/**
 * API error response
 */
export interface ApiErrorResponse {
  message: string;
  code: string | number;
  status: number;
  details?: Record<string, unknown>;
}

/**
 * Component state types
 */
export interface FormState {
  isLoading: boolean;
  error: string | null;
  isSubmitting: boolean;
}

export interface ListState {
  isLoading: boolean;
  error: string | null;
  items: Cliente[];
  total: number;
  page: number;
  limit: number;
}
