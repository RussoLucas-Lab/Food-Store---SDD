/**
 * Toast — Componente individual de notificación.
 *
 * Colores:
 * - success: verde
 * - error: rojo
 * - info: gris neutro
 */

import React from 'react';
import type { Toast as ToastType } from '../../hooks/useToast';

interface ToastProps {
  toast: ToastType;
  onRemove: (id: string) => void;
}

const colorMap: Record<ToastType['type'], string> = {
  success: 'bg-green-600 text-white',
  error: 'bg-red-600 text-white',
  info: 'bg-gray-700 text-white',
};

const iconMap: Record<ToastType['type'], string> = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
};

const Toast: React.FC<ToastProps> = ({ toast, onRemove }) => {
  return (
    <div
      role="alert"
      aria-live="polite"
      className={`flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg text-sm font-medium min-w-[200px] max-w-xs animate-fade-in ${colorMap[toast.type]}`}
    >
      <span className="text-base leading-none">{iconMap[toast.type]}</span>
      <span className="flex-1">{toast.message}</span>
      <button
        onClick={() => onRemove(toast.id)}
        className="ml-2 opacity-70 hover:opacity-100 transition-opacity text-base leading-none"
        aria-label="Cerrar notificación"
      >
        ×
      </button>
    </div>
  );
};

export default Toast;
