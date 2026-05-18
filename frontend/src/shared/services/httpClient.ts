import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

/**
 * Global HTTP Client with automatic token injection and error handling
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000', 10);

// Create axios instance
export const httpClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor: inject JWT token from localStorage
 */
httpClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const stored = localStorage.getItem('auth-store');
    const token = stored ? JSON.parse(stored) : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor: handle 401 errors and token refresh
 */
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string | null) => void; reject: (error: AxiosError) => void }> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  isRefreshing = false;
  failedQueue = [];
};

httpClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const originalRequest = error.config as any;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return httpClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Attempt to refresh token (backend endpoint: POST /auth/refresh)
        const refreshResponse = await axios.post(`${API_URL}/auth/refresh`, {
          token: localStorage.getItem('authToken'),
        });

        const newToken = refreshResponse.data.token;
        localStorage.setItem('authToken', newToken);

        httpClient.defaults.headers.common.Authorization = `Bearer ${newToken}`;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;

        processQueue(null, newToken);
        return httpClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as AxiosError, null);
        localStorage.removeItem('auth-store');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Error handler: transform API errors into consistent format
 */
export interface ApiError {
  message: string;
  code: string | number;
  status: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  details?: Record<string, any>;
}

export const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    return {
      message: error.response?.data?.message || error.message || 'Unknown error',
      code: error.response?.data?.code || error.code || 'UNKNOWN_ERROR',
      status: error.response?.status || 500,
      details: error.response?.data,
    };
  }

  return {
    message: 'Unexpected error',
    code: 'UNEXPECTED_ERROR',
    status: 500,
  };
};

/**
 * Retry logic wrapper for network failures
 */
export const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await new Promise((resolve) => setTimeout(resolve, delay * attempt));
    }
  }
  throw new Error('Max retries exceeded');
};

export default httpClient;
