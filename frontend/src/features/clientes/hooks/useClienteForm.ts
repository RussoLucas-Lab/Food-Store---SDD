import { useState, useCallback } from 'react';
import { FormState } from '../../../shared/types';

/**
 * useClienteForm Hook
 * Manages form state: loading, error, submitting
 * Useful for components that handle form submissions
 */
export const useClienteForm = (initialState: Partial<FormState> = {}) => {
  const [isLoading, setIsLoading] = useState(initialState.isLoading || false);
  const [error, setError] = useState<string | null>(initialState.error || null);
  const [isSubmitting, setIsSubmitting] = useState(initialState.isSubmitting || false);

  const setFormLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  const setFormError = useCallback((err: string | null) => {
    setError(err);
  }, []);

  const setFormSubmitting = useCallback((submitting: boolean) => {
    setIsSubmitting(submitting);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const resetForm = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setIsSubmitting(false);
  }, []);

  return {
    isLoading,
    error,
    isSubmitting,
    setFormLoading,
    setFormError,
    setFormSubmitting,
    clearError,
    resetForm,
  };
};

export default useClienteForm;
