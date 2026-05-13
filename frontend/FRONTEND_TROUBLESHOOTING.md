# Frontend Troubleshooting

Soluciones a problemas comunes del desarrollo frontend.

---

## Server no inicia

### "Port 5173 is already in use"

```bash
# Opción 1: Usar otro puerto
npm run dev -- --port 5174

# Opción 2: Matar proceso en puerto 5173
# Windows PowerShell:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5173
kill -9 <PID>
```

### "ENOSPC: System limit for number of open files exceeded"

El watcher de Vite alcanzó el límite. Aumentá el límite:

```bash
# Linux/macOS
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# macOS (si lo anterior no funciona)
echo kern.maxfiles=65536 | sudo tee /etc/sysctl.conf.d/limits.conf
sudo sysctl -f
```

### "Cannot find module '@/shared/components'"

Path alias no está configurado. Verifica `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Luego reiniciá Vite:
```bash
npm run dev
```

---

## Imports no funcionan

### "Module not found: Error: Can't resolve 'X'"

```
❌ import { Button } from '../../../shared/components/atoms';
✅ import { Button } from '@/shared/components/atoms';
```

Usa el alias `@/*` en lugar de rutas relativas.

---

## Estilos no aplican

### Clases CSS no se aplican a elementos

Verificá que:
1. Importás el archivo CSS/SCSS
2. La clase existe en el archivo
3. La especificidad CSS no es sobrescrita

```typescript
// ✅ Importa el CSS
import './Button.css';

// En Button.tsx
export const Button = () => {
  return <button className="button">Click</button>;
};
```

### Estilos se aplican pero se ven raros

Abrí DevTools (F12) → Elements → verifica:
1. El elemento tiene la clase aplicada
2. El CSS está en `<style>` o `<link>`
3. No hay selectores más específicos que lo sobrescriban

### Variables CSS no funcionan

Variables CSS deben estar definidas en un scope que las contenga:

```css
/* ✅ Correcto: disponible globalmente */
:root {
  --color-primary: #007bff;
  --spacing-md: 12px;
}

.button {
  color: var(--color-primary);
  padding: var(--spacing-md);
}

/* ❌ Incorrecto: variable no definida en :root */
.button {
  color: var(--color-button);  /* ← No definida */
}
```

---

## Tests fallan

### "ReferenceError: document is not defined"

Tests necesitan ambiente DOM. Verifica `vitest.config.ts`:

```typescript
export default defineConfig({
  test: {
    environment: 'jsdom',  // ← Debe estar
  },
});
```

### "Cannot find module in test files"

Aliases no están configurados en vitest. Agrega a `vitest.config.ts`:

```typescript
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### "useContext() returns undefined"

Estás usando un hook que depende de Context pero no renderizaste dentro del provider:

```typescript
// ❌ Incorrecto
render(<MyComponent />);

// ✅ Correcto: usa renderWithProviders
import { renderWithProviders } from '@/test/utils';
renderWithProviders(<MyComponent />);
```

### Mock no funciona

Verifica que estás usando la sintaxis correcta de vi.mock():

```typescript
import { vi } from 'vitest';

// ✅ Correcto
vi.mock('@/shared/services/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Ahora en el test:
import { httpClient } from '@/shared/services/httpClient';
httpClient.get.mockResolvedValue({ data: [] });
```

### "act(...) warnings"

Warnings sobre `act()` significan que hay updates fuera de eventos React. Solución:

```typescript
// ❌ Incorrecto
test('loads data', async () => {
  render(<Component />);
  await waitFor(() => {
    expect(screen.getByText(/loaded/i)).toBeInTheDocument();
  });
});

// ✅ Correcto: usa waitFor o findBy
test('loads data', async () => {
  render(<Component />);
  expect(await screen.findByText(/loaded/i)).toBeInTheDocument();
});
```

---

## Build fallan

### "npm run build" produce errores

1. **Lint errors**: Ejecutá `npm run lint:fix`
2. **Type errors**: Verificá que no hay `any` types
3. **Missing files**: Asegúrate de que imports apunten a archivos que existen

### "dist/ está vacío"

Verifica que `vite.config.ts` está bien configurado:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
});
```

Luego ejecutá:
```bash
npm run build
```

### "dist/index.html no se ve correctamente"

Verifica `public/index.html`:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Food Store</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

## React issues

### "React is not defined" error

Vite + React 17+ no requieren import explícito de React, pero si lo usás:

```typescript
// ✅ Moderno (no requiere import)
export const MyComponent = () => <div>Hello</div>;

// ✅ También válido (si lo importas)
import React from 'react';
export const MyComponent: React.FC = () => <div>Hello</div>;
```

### State updates no se ven reflejados

1. Verificá que estás usando `setState()` correctamente
2. No mutés state directamente:

```typescript
// ❌ Incorrecto: mutando array
const handleAddItem = () => {
  items.push(newItem);  // ← NO HAGAS ESTO
  setItems(items);
};

// ✅ Correcto: crear nuevo array
const handleAddItem = () => {
  setItems([...items, newItem]);
};
```

### useEffect se ejecuta infinitamente

Verificá dependencias:

```typescript
// ❌ Infinito: sin dependencias
useEffect(() => {
  setCount(count + 1);
});

// ✅ Correcto: dependencias correctas
useEffect(() => {
  setCount(0);
}, []);

// ✅ Correcto: incluye dependencias usadas
useEffect(() => {
  console.log(name);
}, [name]);
```

---

## Performance

### App es lenta

1. Abrí DevTools → Performance tab
2. Graba una acción lenta
3. Buscá "Long tasks" (rojo)

Posibles causas:
- **Componentes sin memo**: Envuelve con `React.memo()`
- **useCallback no usado**: Envuelve callbacks que pasan a componentes memoizados
- **API calls no debounceadas**: Usa `setTimeout()` o libería como `lodash.debounce`
- **Listas grandes**: Usa virtualización con libería como `react-window`

---

## Conexión a API

### "Cannot GET /api/clientes" (404)

Verifica:
1. Backend está corriendo (`python -m uvicorn app:app --reload`)
2. `VITE_API_URL` está correcto en `.env.local`
3. La ruta en el backend existe

```typescript
// frontend/src/features/clientes/services/clienteService.ts
const API_ENDPOINT = '/clientes';  // Ruta relativa
// Se expande a: VITE_API_URL + '/clientes'
```

### "401 Unauthorized"

Token JWT expiró o no es válido. El interceptor debería:
1. Intentar refrescar el token
2. Si falla, redirigir a login

Verifica `src/shared/services/httpClient.ts`:

```typescript
// Response interceptor maneja 401
httpClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Intenta refrescar token
      // Si falla, redirige a login
    }
    return Promise.reject(error);
  }
);
```

### "Network error: Failed to fetch"

CORS está rechazando la request. En el backend:

```python
# FastAPI: agrega CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Browser issues

### "Unexpected token <" en console

Script tag en HTML está siendo servido como HTML en lugar de JavaScript. Verifica:
1. `public/index.html` tiene `<script type="module" src="/src/main.tsx">`
2. Vite está sirviendo correctamente: `npm run dev`

### LocalStorage no persiste

Por defecto, localStorage persiste en el navegador. Si no funciona:

```typescript
// Verificá que escribés correctamente
localStorage.setItem('token', token);
const token = localStorage.getItem('token');

// Verifica DevTools → Application → Local Storage
// En incógnito/private, localStorage se borra al cerrar
```

---

## Git issues

### "git add frontend/" no agrega archivos

Verifica que `frontend/` no está en `.gitignore`:

```bash
# Ver qué se ignora
git status

# Si todo parece ignorado:
cat .gitignore | grep frontend
```

---

## Necesitas más ayuda?

1. Buscá en el archivo `frontend/COMPONENT_GUIDE.md`
2. Revisá el código de componentes similares
3. Ejecutá `npm run test` para ver ejemplos de uso
4. Contactá al equipo en Slack/Discord
