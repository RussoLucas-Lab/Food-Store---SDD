/**
 * IngredienteSelector — Lista de ingredientes con checkboxes para excluir.
 *
 * Ingredientes con `es_removible=false` están deshabilitados (no se pueden excluir).
 * Llama `onChange(excluidos: number[])` al cambiar la selección.
 */

import React, { useState } from 'react';
import type { Ingrediente } from '../services/productosApi';

interface IngredienteSelectorProps {
  ingredientes: Ingrediente[];
  onChange: (excluidos: number[]) => void;
}

const IngredienteSelector: React.FC<IngredienteSelectorProps> = ({
  ingredientes,
  onChange,
}) => {
  const [excluidos, setExcluidos] = useState<Set<number>>(new Set());

  if (ingredientes.length === 0) {
    return null;
  }

  const handleToggle = (id: number) => {
    const updated = new Set(excluidos);
    if (updated.has(id)) {
      updated.delete(id);
    } else {
      updated.add(id);
    }
    setExcluidos(updated);
    onChange(Array.from(updated));
  };

  return (
    <div>
      <p className="text-sm font-medium text-gray-700 mb-2">
        Personalizar (excluir ingredientes):
      </p>
      <div className="space-y-1.5">
        {ingredientes.map((ing) => (
          <label
            key={ing.id}
            className={`flex items-center gap-2 text-sm cursor-pointer select-none ${
              !ing.es_removible ? 'opacity-50 cursor-not-allowed' : 'hover:text-blue-700'
            }`}
          >
            <input
              type="checkbox"
              checked={excluidos.has(ing.id)}
              onChange={() => handleToggle(ing.id)}
              disabled={!ing.es_removible}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:cursor-not-allowed"
            />
            <span className="text-gray-700">{ing.nombre}</span>
            {ing.es_alergeno && (
              <span className="text-xs text-amber-600 font-medium">(alérgeno)</span>
            )}
            {!ing.es_removible && (
              <span className="text-xs text-gray-400">(no removible)</span>
            )}
          </label>
        ))}
      </div>
    </div>
  );
};

export default IngredienteSelector;
