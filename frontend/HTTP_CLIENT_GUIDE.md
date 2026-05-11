# HTTP Client Guide

How to use the httpClient for API calls in Food Store frontend.

## Overview

The `httpClient` is a singleton Axios instance configured with:
- **Request interceptor**: Injects JWT token from localStorage
- **Response interceptor**: Handles 401 errors and token refresh
- **Error handler**: Transforms API errors to consistent format
- **Retry logic**: Max 3 retries for network failures

## Basic Usage

### Simple GET Request

```typescript
import { httpClient } from '@/shared/services';

export const getProductos = async () => {
  const { data } = await httpClient.get('/api/productos');
  return data;
};
```

### GET with Parameters

```typescript
export const searchProductos = async (query: string, skip: number = 0, limit: number = 10) => {
  const { data } = await httpClient.get('/api/productos', {
    params: { q: query, skip, limit },
  });
  return data;
};
```

### POST Request

```typescript
export const createProducto = async (producto: Producto) => {
  const { data } = await httpClient.post('/api/productos', producto);
  return data;
};
```

### PUT Request

```typescript
export const updateProducto = async (id: string, changes: Partial<Producto>) => {
  const { data } = await httpClient.put(`/api/productos/${id}`, changes);
  return data;
};
```

### DELETE Request

```typescript
export const deleteProducto = async (id: string) => {
  const { data } = await httpClient.delete(`/api/productos/${id}`);
  return data;
};
```

## Error Handling

All errors are transformed to a consistent format via `handleApiError()`:

```typescript
export interface ApiError {
  message: string;
  code: string | number;
  status: number;
  details?: Record<string, any>;
}
```

Usage:

```typescript
import { httpClient, handleApiError } from '@/shared/services';

try {
  const producto = await httpClient.get('/api/productos/123');
} catch (error) {
  const apiError = handleApiError(error);
  console.error(apiError.message);  // Friendly error message
  console.error(apiError.status);   // HTTP status code
  console.error(apiError.details);  // Additional error info
}
```

## Creating Feature-Specific Services

Create a service file for each feature that uses the httpClient:

```typescript
// src/features/productos/services/productoService.ts
import { httpClient, handleApiError } from '@/shared/services';

export interface Producto {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
}

export const productoService = {
  /**
   * Get all productos with pagination
   */
  async getAll(skip: number = 0, limit: number = 10): Promise<Producto[]> {
    try {
      const { data } = await httpClient.get('/api/productos', {
        params: { skip, limit },
      });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  },

  /**
   * Get single producto by ID
   */
  async getById(id: string): Promise<Producto> {
    try {
      const { data } = await httpClient.get(`/api/productos/${id}`);
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  },

  /**
   * Create new producto
   */
  async create(producto: Omit<Producto, 'id'>): Promise<Producto> {
    try {
      const { data } = await httpClient.post('/api/productos', producto);
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  },

  /**
   * Update existing producto
   */
  async update(id: string, changes: Partial<Producto>): Promise<Producto> {
    try {
      const { data } = await httpClient.put(`/api/productos/${id}`, changes);
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  },

  /**
   * Delete producto
   */
  async delete(id: string): Promise<void> {
    try {
      await httpClient.delete(`/api/productos/${id}`);
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  },

  /**
   * Search productos
   */
  async search(query: string): Promise<Producto[]> {
    try {
      const { data } = await httpClient.get('/api/productos/search', {
        params: { q: query },
      });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  },
};
```

## Using Services in Components

```typescript
// src/features/productos/pages/ProductosPage.tsx
import { useEffect, useState } from 'react';
import { productoService, Producto } from '../services/productoService';

export const ProductosPage = () => {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProductos = async () => {
      try {
        setLoading(true);
        const data = await productoService.getAll();
        setProductos(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load productos');
      } finally {
        setLoading(false);
      }
    };

    loadProductos();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1>Productos</h1>
      {productos.map((p) => (
        <ProductoCard key={p.id} producto={p} />
      ))}
    </div>
  );
};
```

## Custom Hooks for API Calls

Create reusable hooks for common data-fetching patterns:

```typescript
// src/shared/hooks/useFetch.ts
import { useEffect, useState } from 'react';
import { handleApiError } from '@/shared/services';

interface UseFetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useFetch = <T,>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
): UseFetchState<T> => {
  const [state, setState] = useState<UseFetchState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      try {
        const result = await fetchFn();
        if (isMounted) {
          setState({ data: result, loading: false, error: null });
        }
      } catch (error) {
        if (isMounted) {
          const apiError = handleApiError(error);
          setState({ data: null, loading: false, error: apiError.message });
        }
      }
    };

    load();

    return () => {
      isMounted = false;
    };
  }, dependencies);

  return state;
};
```

Usage:

```typescript
const { data: productos, loading, error } = useFetch(
  () => productoService.getAll(),
  []
);
```

## Authentication

The httpClient automatically injects the JWT token from localStorage:

```typescript
// Set token after login
localStorage.setItem('authToken', token);

// httpClient will now send Authorization header
// Authorization: Bearer <token>

// Token is automatically refreshed on 401 responses
```

## Request/Response Interceptors

View the interceptor logic in `src/shared/services/httpClient.ts`:

- **Request**: Injects `Authorization: Bearer <token>` header
- **Response**: Handles 401 with automatic token refresh
- **Error**: Transforms to consistent ApiError format
- **Retry**: Max 3 retries on network failures

## Environment Configuration

API URL is configured via environment variable:

```
VITE_API_URL=http://localhost:8000
```

Change in `.env.local` to switch API endpoints.

## Best Practices

1. **Create service files** - One per feature/module
2. **Use TypeScript** - Define request/response interfaces
3. **Handle errors** - Always use try-catch or .catch()
4. **Use custom hooks** - Extract data-fetching logic
5. **Centralize logic** - Don't make http calls directly in components
6. **Cancel requests** - Cleanup on component unmount
7. **Mock in tests** - Mock httpClient in unit tests
8. **Loading states** - Show spinners during API calls
