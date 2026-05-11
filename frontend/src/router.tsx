import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/shared/context/AuthContext';
import { Layout } from '@/shared/components/organisms';

/**
 * ProtectedRoute: Wrapper that checks authentication and role
 */
const ProtectedRoute: React.FC<{ requiredRole?: 'ADMIN' | 'USER' }> = ({
  requiredRole = 'USER',
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

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

        {/* Protected routes with layout */}
        <Route element={<LayoutRoute />}>
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/productos/*" element={<ProductosLayout />} />
            <Route path="/clientes/*" element={<ClientesLayout />} />
          </Route>

          {/* Admin routes */}
          <Route element={<ProtectedRoute requiredRole="ADMIN" />}>
            <Route path="/admin/*" element={<AdminLayout />} />
          </Route>
        </Route>

        {/* Error routes */}
        <Route path="/unauthorized" element={<UnauthorizedPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};

// Placeholder page components
const HomePage: React.FC = () => <div className="p-8"><h1>Welcome to Food Store</h1></div>;
const LoginPage: React.FC = () => <div className="p-8"><h1>Login</h1></div>;
const RegisterPage: React.FC = () => <div className="p-8"><h1>Register</h1></div>;
const AboutPage: React.FC = () => <div className="p-8"><h1>About</h1></div>;
const ProfilePage: React.FC = () => <div className="p-8"><h1>Your Profile</h1></div>;
const ProductosLayout: React.FC = () => <Outlet />;
const ClientesLayout: React.FC = () => <Outlet />;
const AdminLayout: React.FC = () => <Outlet />;
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
