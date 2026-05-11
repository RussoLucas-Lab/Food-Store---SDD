# Frontend Setup Guide

## Overview

This is a **Vite + React + TypeScript** frontend for the Food Store application. The architecture follows **Atomic Design** principles with a scalable component structure and context-based global state management.

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── shared/            # Reusable components, hooks, services, context
│   │   ├── components/
│   │   │   ├── atoms/     # Button, Input, Label, Text
│   │   │   ├── molecules/ # FormField, Card, LoadingSpinner, ErrorMessage
│   │   │   └── organisms/ # Header, Sidebar, Footer, Layout, Modal
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # httpClient, API utilities
│   │   ├── context/       # AuthContext, ThemeContext, NotificationContext
│   │   └── index.ts       # Barrel exports
│   ├── features/          # Feature-specific code
│   │   ├── auth/
│   │   ├── productos/
│   │   ├── clientes/
│   │   └── admin/
│   ├── types/             # Global TypeScript types
│   ├── router.tsx         # Route configuration
│   ├── App.tsx            # Root component
│   └── main.tsx           # Entry point
│   └── test/              # Test utilities and setup
├── vitest.config.ts       # Vitest configuration
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
└── package.json
```

## Tech Stack

- **Bundler**: Vite 8
- **Framework**: React 18
- **Language**: TypeScript 5
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **State Management**: React Context API
- **Testing**: Vitest + @testing-library/react
- **Linting**: ESLint v10 + TypeScript ESLint

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Starts the dev server at `http://localhost:5173` with hot module replacement (HMR).

### Building

```bash
npm run build
```

Generates production build in `dist/` folder.

### Testing

```bash
npm run test
```

Runs all tests in watch mode.

### Linting

```bash
npm run lint
```

Checks code for linting errors.

## Architecture Patterns

### 1. Atomic Design Components

- **Atoms**: Basic building blocks (Button, Input, Label, Text)
- **Molecules**: Combinations of atoms (FormField, Card, LoadingSpinner)
- **Organisms**: Complex, full-featured components (Header, Layout, Modal)

### 2. Context-Based State Management

Three main contexts:
- **AuthContext**: User authentication, token, role
- **ThemeContext**: Light/dark mode toggle
- **NotificationContext**: Toast notifications

Use the corresponding hooks to consume context:

```typescript
const { user, isAuthenticated, login, logout } = useAuth();
const { theme, toggleTheme } = useTheme();
const { notify, notifications, removeNotification } = useNotification();
```

### 3. Feature-Based Organization

Each feature folder (`auth/`, `productos/`, etc.) contains:
- `components/` - Feature-specific components
- `pages/` - Full-page components
- `hooks/` - Feature-specific hooks
- `services/` - API calls for this feature
- `index.ts` - Barrel export

### 4. Protected Routes

Use `ProtectedRoute` wrapper to guard routes:

```typescript
<ProtectedRoute roles={['ADMIN']}>
  <AdminPanel />
</ProtectedRoute>
```

## Environment Variables

Create `.env.local` with:

```
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_APP_NAME=Food Store
```

See `.env.example` for all available variables.

## HTTP Client Setup

The `httpClient` (singleton Axios instance) includes:

- **Request interceptor**: Injects JWT token from localStorage
- **Response interceptor**: Handles 401 errors and token refresh
- **Error handler**: Transforms API errors to consistent format
- **Retry logic**: Max 3 retries for network failures

Usage:

```typescript
import { httpClient } from '@/shared/services';

const { data } = await httpClient.get('/api/productos');
```

## Testing

### Test Utilities

`src/test/setup.ts` provides:
- Global test setup (mocks, fixtures)
- `renderWithProviders()` - Render components with all providers
- `mockHttpClient()` - Mock the HTTP client

### Example Tests

```typescript
import { render, screen } from '@testing-library/react';
import { Button } from '@/shared/components/atoms';

it('renders button', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

## Conventions

- **Components**: PascalCase
- **Hooks**: camelCase starting with `use`
- **Files**: Match component name (e.g., `Button.tsx` for Button component)
- **Exports**: Use barrel exports in `index.ts` for each folder
- **Types**: Define in `.tsx` files or `src/types/` for global types
- **Styling**: CSS modules or inline styles (no CSS-in-JS framework by default)

## Next Steps

- Check `COMPONENT_GUIDE.md` to understand how to create components
- Check `ROUTING_GUIDE.md` to set up new routes
- Check `HTTP_CLIENT_GUIDE.md` to make API calls
