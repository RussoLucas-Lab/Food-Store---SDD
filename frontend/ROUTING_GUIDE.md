# Routing Guide

How to set up routes and protected routes in Food Store frontend.

## Route Configuration

All routes are defined in `src/router.tsx`:

```typescript
// src/router.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/shared/components/ProtectedRoute';
import { Layout } from '@/shared/components/organisms/Layout';

// Pages
import { LoginPage } from '@/features/auth/pages';
import { ProductosPage } from '@/features/productos/pages';
import { ClientesPage } from '@/features/clientes/pages';
import { AdminPage } from '@/features/admin/pages';
import { NotFoundPage } from '@/pages/NotFoundPage';

export const Router = () => (
  <BrowserRouter>
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/about" element={<AboutPage />} />

      {/* Protected Routes with Layout */}
      <Route element={<Layout />}>
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route
          path="/productos"
          element={
            <ProtectedRoute roles={['USER', 'ADMIN']}>
              <ProductosPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/clientes"
          element={
            <ProtectedRoute roles={['ADMIN']}>
              <ClientesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={['ADMIN']}>
              <AdminPage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Error Routes */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </BrowserRouter>
);
```

## Public Routes

Routes accessible to anyone (no auth required):

```typescript
<Route path="/" element={<HomePage />} />
<Route path="/login" element={<LoginPage />} />
<Route path="/register" element={<RegisterPage />} />
<Route path="/about" element={<AboutPage />} />
```

## Protected Routes

Routes that require authentication and optionally specific roles:

### Basic Protected Route

Requires user to be authenticated:

```typescript
<Route
  path="/profile"
  element={
    <ProtectedRoute>
      <ProfilePage />
    </ProtectedRoute>
  }
/>
```

### Role-Based Protected Route

Requires specific roles (ADMIN, USER, GUEST):

```typescript
<Route
  path="/admin"
  element={
    <ProtectedRoute roles={['ADMIN']}>
      <AdminPage />
    </ProtectedRoute>
  }
/>
```

Multiple roles:

```typescript
<Route
  path="/productos"
  element={
    <ProtectedRoute roles={['USER', 'ADMIN']}>
      <ProductosPage />
    </ProtectedRoute>
  }
/>
```

## Layout Route

Wraps protected routes with Header, Sidebar, Footer:

```typescript
<Route element={<Layout />}>
  <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
  <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
</Route>
```

All nested routes will have the Layout applied.

## ProtectedRoute Component

Source: `src/shared/components/ProtectedRoute.tsx`

```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, roles }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !user?.role) {
    return <Navigate to="/unauthorized" replace />;
  }

  if (roles && !roles.includes(user?.role!)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

## Navigation

### Programmatic Navigation

Use `useNavigate` hook:

```typescript
import { useNavigate } from 'react-router-dom';

export const LoginPage = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    // API call...
    navigate('/dashboard');
  };

  return <button onClick={handleLogin}>Login</button>;
};
```

### Link Navigation

Use `<Link>` or `<NavLink>`:

```typescript
import { Link, NavLink } from 'react-router-dom';

export const Navigation = () => {
  return (
    <nav>
      <Link to="/">Home</Link>
      <NavLink to="/productos" className={({ isActive }) => isActive ? 'active' : ''}>
        Productos
      </NavLink>
    </nav>
  );
};
```

## Role-Based Visibility

Show/hide links based on user role:

```typescript
import { useAuth } from '@/shared/context';

export const Navigation = () => {
  const { user } = useAuth();

  return (
    <nav>
      <Link to="/productos">Productos</Link>
      {user?.role === 'ADMIN' && <Link to="/admin">Admin Panel</Link>}
    </nav>
  );
};
```

## Error Pages

### 404 Not Found

```typescript
// src/pages/NotFoundPage.tsx
export const NotFoundPage = () => {
  const navigate = useNavigate();
  return (
    <div className="error-page">
      <h1>404</h1>
      <p>Page not found</p>
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};
```

### 403 Unauthorized

```typescript
// src/pages/UnauthorizedPage.tsx
export const UnauthorizedPage = () => {
  const navigate = useNavigate();
  return (
    <div className="error-page">
      <h1>403</h1>
      <p>You don't have permission to access this page</p>
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};
```

## Adding New Routes

1. **Create the page component**

```typescript
// src/features/myfeature/pages/MyPage.tsx
export const MyPage = () => {
  return <div>My Page</div>;
};
```

2. **Export from feature index**

```typescript
// src/features/myfeature/index.ts
export { MyPage } from './pages/MyPage';
```

3. **Add route to router.tsx**

```typescript
import { MyPage } from '@/features/myfeature';

<Route path="/myroute" element={<ProtectedRoute><MyPage /></ProtectedRoute>} />
```

## Best Practices

1. **Always protect admin routes** - Use role-based protection
2. **Redirect on login** - Take users to dashboard, not home
3. **Preserve auth state** - Use localStorage for token persistence
4. **Handle token expiry** - Refresh token or redirect to login
5. **Use Layout wrapper** - Keep header/sidebar consistent
6. **Nested routes** - Use layout wrapper for persistent UI
