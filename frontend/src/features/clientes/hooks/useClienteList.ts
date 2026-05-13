import { useState, useCallback } from 'react';
import { Cliente, ListState } from '../../../shared/types';

const INITIAL_LIST_STATE: ListState = {
  isLoading: false,
  error: null,
  items: [],
  total: 0,
  page: 1,
  limit: 10,
};

/**
 * useClienteList Hook
 * Manages list state: loading, error, items, pagination
 * Useful for components that display cliente lists
 */
export const useClienteList = (initialState: Partial<ListState> = {}) => {
  const [state, setState] = useState<ListState>({
    ...INITIAL_LIST_STATE,
    ...initialState,
  });

  const setListLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, isLoading: loading }));
  }, []);

  const setListError = useCallback((err: string | null) => {
    setState((prev) => ({ ...prev, error: err }));
  }, []);

  const setListItems = useCallback((items: Cliente[]) => {
    setState((prev) => ({ ...prev, items }));
  }, []);

  const setListPagination = useCallback((page: number, limit: number, total: number) => {
    setState((prev) => ({ ...prev, page, limit, total }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const resetList = useCallback(() => {
    setState(INITIAL_LIST_STATE);
  }, []);

  return {
    ...state,
    setListLoading,
    setListError,
    setListItems,
    setListPagination,
    clearError,
    resetList,
  };
};

export default useClienteList;
