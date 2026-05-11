import React from 'react';
import { ContextProviders } from '@/shared/context';
import AppRouter from '@/router';
import { useNotification } from '@/shared/context/NotificationContext';

/**
 * Toast Notifier: Displays notifications from context
 */
const ToastNotifier: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  return (
    <div className="fixed top-4 right-4 space-y-2 z-40">
      {notifications.map((notif) => {
        const bgColor = {
          success: 'bg-green-500',
          error: 'bg-red-500',
          info: 'bg-blue-500',
          warning: 'bg-yellow-500',
        }[notif.type];

        return (
          <div
            key={notif.id}
            className={`${bgColor} text-white px-4 py-3 rounded shadow-lg flex items-center justify-between`}
          >
            <span>{notif.message}</span>
            <button
              onClick={() => removeNotification(notif.id)}
              className="ml-4 text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
};

/**
 * App: Main application component
 */
const App: React.FC = () => {
  return (
    <ContextProviders>
      <ToastNotifier />
      <AppRouter />
    </ContextProviders>
  );
};

export default App;
