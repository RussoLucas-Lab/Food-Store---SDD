/**
 * ToastContainer — Contenedor de notificaciones toast.
 *
 * Posición fija en bottom-right con z-50.
 * Registra el showToast globalmente para acceso fuera del árbol React.
 */

import React, { useEffect } from 'react';
import Toast from '../atoms/Toast';
import { useToast, registerGlobalToast } from '../../hooks/useToast';

const ToastContainer: React.FC = () => {
  const { toasts, showToast, removeToast } = useToast();

  // Registrar función global para uso fuera de componentes
  useEffect(() => {
    registerGlobalToast(showToast);
  }, [showToast]);

  if (toasts.length === 0) return null;

  return (
    <div
      aria-label="Notificaciones"
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 items-end"
    >
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onRemove={removeToast} />
      ))}
    </div>
  );
};

export default ToastContainer;
