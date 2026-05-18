/**
 * AdminLayout — Layout principal del panel de administración.
 *
 * Compone AdminNav (barra lateral) + área de contenido (Outlet de rutas).
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import AdminNav from '../components/AdminNav';

/**
 * AdminLayout wraps all admin pages with the side navigation.
 */
const AdminLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <AdminNav />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
