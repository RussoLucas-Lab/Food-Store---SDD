import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

export interface HeaderProps {
  onMenuToggle?: () => void;
}

/**
 * Header: Top navigation bar with logo, nav links, user menu, theme toggle
 */
export const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-blue-600 text-white p-4 shadow-md">
      <div className="flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuToggle}
            className="lg:hidden p-2 hover:bg-blue-700 rounded"
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <h1 className="text-2xl font-bold">Food Store</h1>
        </div>

        <nav className="hidden md:flex gap-6">
          <a href="/" className="hover:text-blue-200">
            Home
          </a>
          {isAuthenticated && <a href="/productos">Productos</a>}
          {isAuthenticated && <a href="/clientes">Clientes</a>}
          {user?.role === 'ADMIN' && <a href="/admin">Admin</a>}
        </nav>

        <div className="flex items-center gap-4">
          <button
            onClick={toggleTheme}
            className="p-2 hover:bg-blue-700 rounded"
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>

          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <span className="text-sm">{user?.nombre}</span>
              <button
                onClick={logout}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded"
              >
                Logout
              </button>
            </div>
          ) : (
            <a href="/login" className="px-3 py-1 bg-white text-blue-600 rounded font-semibold">
              Login
            </a>
          )}
        </div>
      </div>
    </header>
  );
};

/**
 * Sidebar: Navigation menu with role-based visibility
 */
export const Sidebar: React.FC<{ isOpen?: boolean; _onClose?: () => void }> = ({
  isOpen = true,
  _onClose,
}) => {
  const { user } = useAuth();

  return (
    <aside
      className={`${
        isOpen ? 'w-64' : 'w-0'
      } bg-gray-800 text-white transition-all duration-300 overflow-hidden`}
    >
      <nav className="p-4 space-y-2">
        <a href="/" className="block p-2 hover:bg-gray-700 rounded">
          Dashboard
        </a>
        <a href="/productos" className="block p-2 hover:bg-gray-700 rounded">
          Productos
        </a>
        <a href="/clientes" className="block p-2 hover:bg-gray-700 rounded">
          Clientes
        </a>
        {user?.role === 'ADMIN' && (
          <>
            <hr className="my-2" />
            <a href="/admin" className="block p-2 hover:bg-gray-700 rounded">
              Admin Panel
            </a>
          </>
        )}
      </nav>
    </aside>
  );
};

/**
 * Footer: Bottom bar with copyright and links
 */
export const Footer: React.FC = () => (
  <footer className="bg-gray-800 text-gray-300 p-4 text-center text-sm">
    <p>&copy; 2026 Food Store. All rights reserved.</p>
  </footer>
);

/**
 * Layout: Main layout wrapper combining Header, Sidebar, main content, Footer
 */
export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div className="flex flex-col min-h-screen">
      <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 overflow-auto bg-gray-50 p-4">{children}</main>
      </div>
      <Footer />
    </div>
  );
};

/**
 * Modal: Dialog box with overlay
 */
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black opacity-50"
        onClick={onClose}
        role="presentation"
      ></div>
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
          aria-label="Close modal"
        >
          ✕
        </button>
        {title && <h2 className="text-xl font-bold mb-4">{title}</h2>}
        {children}
      </div>
    </div>
  );
};
