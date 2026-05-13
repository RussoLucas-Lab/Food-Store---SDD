# Frontend - Food Store

Cliente React desarrollado con **Vite**, **TypeScript**, **React Router** y **Context API**.

---

## Setup del entorno

### Requisitos previos

- Node.js 18+
- npm 9+

### Instalación

```bash
cd frontend
npm install
```

### Scripts disponibles

```bash
# Desarrollo con HMR
npm run dev          # inicia servidor en http://localhost:5173

# Testing
npm run test         # ejecuta tests con vitest
npm run test:ui      # abre interfaz visual de tests

# Calidad de código
npm run lint         # ejecuta eslint
npm run lint:fix     # auto-corrige errores de linting

# Build para producción
npm run build        # genera carpeta dist/
npm run preview      # preview del build
```

---

## Arquitectura

### Estructura de carpetas

```
src/
├── features/
│   ├── auth/          # Módulo de autenticación
│   ├── productos/     # Módulo de productos
│   ├── clientes/      # Módulo de clientes
│   └── admin/         # Panel administrativo
├── shared/
│   ├── components/    # Componentes reutilizables (atoms, molecules, organisms)
│   ├── context/       # Context API providers (Auth, Theme, Notification)
│   ├── hooks/         # Custom React hooks
│   ├── services/      # HTTP client y utilidades
│   └── types/         # Tipos TypeScript compartidos
├── router.tsx         # Configuración de rutas
├── App.tsx            # Componente raíz
└── main.tsx           # Punto de entrada

public/
└── index.html         # HTML base

vite.config.ts         # Configuración de Vite
tsconfig.json          # Configuración de TypeScript
vitest.config.ts       # Configuración de tests
.eslintrc.json         # Configuración de ESLint
.prettierrc            # Configuración de Prettier
```

### Patrones arquitectónicos

**Atomic Design**: Los componentes se organizan en 3 niveles de complejidad:
- **Atoms**: Componentes básicos (Button, Input, Label, Text)
- **Molecules**: Componentes compuestos (FormField, Card, LoadingSpinner)
- **Organisms**: Componentes complejos (Header, Sidebar, Layout, Modal)

**Feature-based Structure**: Cada feature (auth, productos, clientes) es independiente con:
- `components/` — Componentes de la feature
- `pages/` — Páginas (rutas)
- `hooks/` — Hooks personalizados
- `services/` — HTTP calls a la API
- `index.ts` — Barrel export

**Global State**: Context API + localStorage para:
- **AuthContext** — Usuario actual, token, roles
- **ThemeContext** — Preferencia de tema (light/dark)
- **NotificationContext** — Toasts/notificaciones

---

## Documentación detallada

Lee los siguientes documentos para entender los patrones y convenciones:

| Archivo | Descripción |
|---------|-------------|
| `FRONTEND_SETUP.md` | Estructura del proyecto y convenciones de nombres |
| `COMPONENT_GUIDE.md` | Cómo crear atoms, molecules y organisms |
| `HTTP_CLIENT_GUIDE.md` | Cómo usar httpClient para llamadas API |
| `ROUTING_GUIDE.md` | Cómo agregar rutas públicas, protegidas y admin |

---

## Desarrollo

### Hot Module Replacement (HMR)

Vite proporciona HMR automático. Guardá archivos y verás cambios en el navegador al instante.

### Type Safety

TypeScript está configurado en modo strict. Siempre usá tipos explícitos:

```typescript
const user: User = fetchUser();  // ✅ Explícito
```

### Componentes

Ejemplo de un componente con tipos:

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  onClick,
  disabled = false,
  children,
}) => {
  return (
    <button className={`btn btn--${variant} btn--${size}`} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
};
```

### Context & Hooks

Usa Context API para estado global. Ejemplo:

```typescript
// AuthContext
const { user, token, login, logout, hasRole } = useAuth();

// ThemeContext
const { theme, toggleTheme } = useTheme();

// NotificationContext
const { showNotification } = useNotification();
```

### HTTP Client

Usa `httpClient` (singleton de Axios) con request/response interceptors:

```typescript
import { httpClient } from '@/shared/services';

const response = await httpClient.get('/clientes');
// Automáticamente inyecta JWT, retry, error handling
```

---

## Testing

### Setup de tests

Tests están configurados con **Vitest** + **@testing-library**.

Utilidades:
- `renderWithProviders()` — Renderiza componentes con Context providers
- `mockHttpClient()` — Mock del httpClient para tests

### Ejemplo de test

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '@/shared/components/atoms';

test('Button renders with correct text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});

test('Button calls onClick handler', async () => {
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Click me</Button>);
  
  const button = screen.getByText('Click me');
  await userEvent.click(button);
  
  expect(handleClick).toHaveBeenCalledOnce();
});
```

### Cobertura

Ejecutá tests con cobertura:

```bash
npm run test -- --coverage
```

---

## Build y Deploy

### Build para producción

```bash
npm run build
```

Genera la carpeta `dist/` lista para deploy.

### Preview del build

```bash
npm run preview
```

Ejecuta servidor local sirviendo el build.

### Environment variables

Define variables en `.env.local`:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_APP_NAME=Food Store
```

Las variables accesibles en el código deben estar prefijadas con `VITE_`.

---

## Troubleshooting

### Puerto 5173 ya está en uso

```bash
npm run dev -- --port 5174
```

### Module not found errors

Verifica que las rutas en `tsconfig.json` están correctas. El alias `@/*` apunta a `src/*`.

### Estilos no aplican

- Verifica que importás el archivo CSS/SCSS
- Chequea que los selectores están correctos
- Abre DevTools → Elements para verificar que el CSS está aplicado

### Tests fallan

- Ejecutá `npm run test -- --reporter=verbose` para más detalles
- Verifica que mocks estén configurados en `test/setup.ts`
- Asegúrate de usar `renderWithProviders()` para componentes que usan Context

---

## Contribución

Seguí las convenciones en `COMPONENT_GUIDE.md` al crear componentes nuevos.

Antes de pushear:
1. `npm run lint` — verifica linting
2. `npm run test` — ejecuta tests
3. `npm run build` — verifica que el build sea exitoso

---

## Links

- [Vite](https://vitejs.dev)
- [React](https://react.dev)
- [React Router](https://reactrouter.com)
- [TypeScript](https://www.typescriptlang.org)
- [Vitest](https://vitest.dev)
- [Testing Library](https://testing-library.com)

---

## Equipo

Food Store Frontend — 2026
