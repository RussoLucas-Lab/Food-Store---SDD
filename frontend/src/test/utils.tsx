import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ContextProviders } from '@/shared/context';
import { vi } from 'vitest';
import httpClient from '@/shared/services/httpClient';

/**
 * renderWithProviders: Render component with all context providers
 */
export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <ContextProviders>{children}</ContextProviders>
  );

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * mockHttpClient: Mock the HTTP client for tests
 */
export function mockHttpClient() {
  const mock = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  };

  vi.spyOn(httpClient, 'get').mockImplementation(mock.get);
  vi.spyOn(httpClient, 'post').mockImplementation(mock.post);
  vi.spyOn(httpClient, 'put').mockImplementation(mock.put);
  vi.spyOn(httpClient, 'patch').mockImplementation(mock.patch);
  vi.spyOn(httpClient, 'delete').mockImplementation(mock.delete);

  return mock;
}

export * from '@testing-library/react';
export { userEvent } from '@testing-library/user-event';
