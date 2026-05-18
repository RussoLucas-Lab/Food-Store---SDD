/**
 * AdminNav — Navegación del panel de administración.
 *
 * Muestra los enlaces filtrados según el rol del usuario:
 * - ADMIN: Dashboard, Usuarios, Catálogo, Stock, Despacho
 * - STOCK: Catálogo, Stock
 * - PEDIDOS: Despacho
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '@/shared/context/AuthContext';

interface NavItem {
  to: string;
  label: string;
  roles: string[];
}

const NAV_ITEMS: NavItem[] = [
  { to: '/admin/dashboard', label: 'Dashboard', roles: ['ADMIN'] },
  { to: '/admin/usuarios', label: 'Usuarios', roles: ['ADMIN'] },
  { to: '/admin/categorias', label: 'Categorías', roles: ['ADMIN', 'STOCK'] },
  { to: '/admin/ingredientes', label: 'Ingredientes', roles: ['ADMIN', 'STOCK'] },
  { to: '/admin/productos', label: 'Productos', roles: ['ADMIN', 'STOCK'] },
  { to: '/admin/stock', label: 'Stock', roles: ['ADMIN', 'STOCK'] },
  { to: '/admin/despacho', label: 'Despacho', roles: ['ADMIN', 'PEDIDOS'] },
];

/**
 * AdminNav renders role-filtered navigation links.
 */
const AdminNav: React.FC = () => {
  const { user } = useAuth();
  const userRole = user?.role ?? '';

  // Map AuthContext role to admin nav roles
  const effectiveRole = userRole === 'USER' ? 'CLIENT' : userRole;

  const visibleItems = NAV_ITEMS.filter((item) =>
    item.roles.includes(effectiveRole) || item.roles.includes(userRole)
  );

  return (
    <nav
      className="bg-gray-800 text-white w-56 min-h-screen flex flex-col py-6"
      aria-label="Admin navigation"
    >
      <div className="px-4 mb-6">
        <h2 className="text-lg font-semibold text-white">Panel Admin</h2>
        {user && (
          <p className="text-xs text-gray-400 mt-1">
            {user.email} ({effectiveRole})
          </p>
        )}
      </div>

      <ul className="flex flex-col gap-1 px-2">
        {visibleItems.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `block px-3 py-2 rounded text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default AdminNav;
