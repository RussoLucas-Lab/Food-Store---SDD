import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, useParams, Link } from 'react-router-dom';
import { useAuth } from '@/shared/context/AuthContext';
import { Layout } from '@/shared/components/organisms';
import { LoginPage, RegisterPage } from '@/features/auth/pages';
import {
  ClientesPage,
  ClienteCreatePage,
  ClienteDetailPage,
  PerfilPage,
} from '@/features/clientes/pages';
import CheckoutPage from '@/features/pedidos/pages/CheckoutPage';
import PaymentPage from '@/features/pedidos/pages/PaymentPage';
import GestionPedidosPage from '@/features/pedidos/pages/GestionPedidosPage';
import MisPedidosPage from '@/features/pedidos/pages/MisPedidosPage';
import AdminLayoutPage from '@/features/admin/pages/AdminLayout';
import DashboardPage from '@/features/admin/pages/DashboardPage';
import UsuariosPage from '@/features/admin/pages/UsuariosPage';
import CategoriasAdminPage from '@/features/admin/pages/CategoriasAdminPage';
import IngredientesAdminPage from '@/features/admin/pages/IngredientesAdminPage';
import ProductosAdminPage from '@/features/admin/pages/ProductosAdminPage';
import StockPage from '@/features/admin/pages/StockPage';
import { CatalogoPage, ProductoDetailPage } from '@/features/productos/pages';

/**
 * ProtectedRoute: Wrapper that checks authentication and role.
 * Supports requiredRoles array for multi-role access (e.g., PEDIDOS + ADMIN).
 */
const ProtectedRoute: React.FC<{
  requiredRole?: 'ADMIN' | 'USER';
  requiredRoles?: string[];
}> = ({ requiredRole = 'USER', requiredRoles }) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Multi-role check (for PEDIDOS/ADMIN routes)
  if (requiredRoles && requiredRoles.length > 0) {
    const userRole = user?.role ?? '';
    if (!requiredRoles.includes(userRole)) {
      return <Navigate to="/unauthorized" replace />;
    }
    return <Outlet />;
  }

  // Legacy single-role check
  if (requiredRole === 'ADMIN' && user?.role !== 'ADMIN') {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
};

/**
 * LayoutRoute: Wrapper that applies main Layout
 */
const LayoutRoute: React.FC = () => (
  <Layout>
    <Outlet />
  </Layout>
);

/**
 * App Router: Defines all routes
 */
export const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/about" element={<AboutPage />} />

        {/* Productos — público (catálogo sin login), envuelto en Layout */}
        <Route element={<LayoutRoute />}>
          <Route path="/productos" element={<CatalogoPage />} />
          <Route path="/productos/:id" element={<ProductoDetailPage />} />
        </Route>

        {/* Protected routes with layout */}
        <Route element={<LayoutRoute />}>
          <Route element={<ProtectedRoute />}>
            {/* /profile → redirigir a /perfil */}
            <Route path="/profile" element={<Navigate to="/perfil" replace />} />
            <Route path="/perfil" element={<PerfilPage />} />
            {/* Clientes routes */}
            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/clientes/crear" element={<ClienteCreatePage />} />
            <Route path="/clientes/:id" element={<ClienteDetailPage />} />
            <Route path="/clientes/:id/editar" element={<ClienteDetailPage />} />
            {/* Pedidos / Checkout routes */}
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/pedidos/:id" element={<PedidoConfirmacionPage />} />
            {/* Payment route — protected, CLIENT only */}
            <Route path="/pedidos/:id/pago" element={<PaymentPage />} />
          </Route>

          {/* Mis Pedidos — CLIENT (USER) */}
          <Route element={<ProtectedRoute />}>
            <Route path="/mis-pedidos" element={<MisPedidosPage />} />
          </Route>

          {/* Gestión de pedidos — PEDIDOS y ADMIN */}
          <Route element={<ProtectedRoute requiredRoles={['ADMIN', 'PEDIDOS']} />}>
            <Route path="/gestion/pedidos" element={<GestionPedidosPage />} />
          </Route>

          {/* Admin panel — ADMIN, STOCK, PEDIDOS */}
          <Route
            element={
              <ProtectedRoute requiredRoles={['ADMIN', 'STOCK', 'PEDIDOS']} />
            }
          >
            <Route path="/admin" element={<AdminLayoutPage />}>
              <Route index element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="usuarios" element={<UsuariosPage />} />
              {/* Catalog management — three separate pages */}
              <Route path="categorias" element={<CategoriasAdminPage />} />
              <Route path="ingredientes" element={<IngredientesAdminPage />} />
              <Route path="productos" element={<ProductosAdminPage />} />
              {/* Redirect legacy /admin/catalogo → /admin/categorias */}
              <Route path="catalogo" element={<Navigate to="/admin/categorias" replace />} />
              <Route path="stock" element={<StockPage />} />
              <Route path="despacho" element={<GestionPedidosPage />} />
            </Route>
          </Route>
        </Route>

        {/* Error routes */}
        <Route path="/unauthorized" element={<UnauthorizedPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};

// ── Páginas estáticas ─────────────────────────────────────────────────────────

/**
 * HomePage — Landing page con hero section y CTA al catálogo.
 */
const HomePage: React.FC = () => (
  <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
    {/* Hero */}
    <div className="max-w-4xl mx-auto px-4 pt-24 pb-16 text-center">
      <h1 className="text-5xl font-extrabold text-gray-900 mb-6">
        🍽️ Food Store
      </h1>
      <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
        Pedí tus comidas favoritas desde casa. Catálogo fresco, entregas rápidas
        y el mejor sabor directo a tu puerta.
      </p>
      <Link
        to="/productos"
        className="inline-block bg-blue-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-blue-700 transition-colors shadow-md"
      >
        Ver catálogo →
      </Link>
    </div>

    {/* Features */}
    <div className="max-w-5xl mx-auto px-4 pb-24 grid grid-cols-1 sm:grid-cols-3 gap-8 text-center">
      {[
        { icon: '🥗', title: 'Ingredientes frescos', desc: 'Productos seleccionados cada día.' },
        { icon: '🚀', title: 'Entrega rápida', desc: 'En tu puerta en tiempo récord.' },
        { icon: '💳', title: 'Pago seguro', desc: 'MercadoPago y más opciones.' },
      ].map((f) => (
        <div key={f.title} className="p-6 bg-white rounded-xl shadow-sm">
          <div className="text-4xl mb-3">{f.icon}</div>
          <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
          <p className="text-sm text-gray-500">{f.desc}</p>
        </div>
      ))}
    </div>
  </div>
);

/**
 * PedidoConfirmacionPage — Confirmación del pedido creado.
 * Muestra ID del pedido, estado PENDIENTE y links de navegación.
 */
const PedidoConfirmacionPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="max-w-xl mx-auto py-16 text-center px-4">
      <div className="text-6xl mb-6">🎉</div>
      <h1 className="text-3xl font-bold text-green-600 mb-3">
        ¡Pedido creado!
      </h1>
      {id && (
        <p className="text-gray-500 text-sm mb-2">
          Número de pedido: <span className="font-semibold text-gray-900">#{id}</span>
        </p>
      )}
      <p className="text-gray-600 mb-2">
        Estado: <span className="inline-block font-medium text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded">PENDIENTE</span>
      </p>
      <p className="text-sm text-gray-500 mb-8">
        Te notificaremos cuando sea confirmado por el sistema.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link
          to="/mis-pedidos"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Ver mis pedidos
        </Link>
        <Link
          to="/productos"
          className="inline-block border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
        >
          Seguir comprando
        </Link>
      </div>
    </div>
  );
};

const AboutPage: React.FC = () => <div className="p-8"><h1>About</h1></div>;

const UnauthorizedPage: React.FC = () => (
  <div className="p-8 text-center">
    <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
    <p>You don't have permission to access this page.</p>
  </div>
);

const NotFoundPage: React.FC = () => (
  <div className="p-8 text-center">
    <h1 className="text-2xl font-bold text-gray-600">404 - Not Found</h1>
    <p>Page not found.</p>
  </div>
);

export default AppRouter;
