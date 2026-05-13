import React, { useState, useCallback, useEffect } from 'react';
import { Input, Button } from '../../../shared/components/atoms';
import './ClienteSearch.css';

interface ClienteSearchProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  debounceMs?: number;
}

/**
 * ClienteSearch Component
 * Search bar for filtering clientes by name or email
 * - Debounced input to reduce API calls
 * - Integrates with parent component for search functionality
 * - Admin-only feature
 */
export const ClienteSearch: React.FC<ClienteSearchProps> = ({
  onSearch,
  isLoading = false,
  placeholder = 'Buscar por nombre o email...',
  debounceMs = 300,
}) => {
  const [query, setQuery] = useState('');
  const [debounceTimer, setDebounceTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  /**
   * Debounced search: wait for user to stop typing before triggering search
   */
  useEffect(() => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const timer = setTimeout(() => {
      onSearch(query);
    }, debounceMs);

    setDebounceTimer(timer);

    return () => {
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [query, debounceMs, onSearch]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleClear = useCallback(() => {
    setQuery('');
    onSearch('');
  }, [onSearch]);

  return (
    <div className="cliente-search">
      <div className="cliente-search__container">
        <Input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={handleChange}
          disabled={isLoading}
          className="cliente-search__input"
        />
        {query && (
          <Button
            type="button"
            variant="secondary"
            onClick={handleClear}
            disabled={isLoading}
            className="cliente-search__clear"
          >
            ✕
          </Button>
        )}
      </div>
      {isLoading && <p className="cliente-search__status">Buscando...</p>}
    </div>
  );
};

export default ClienteSearch;
