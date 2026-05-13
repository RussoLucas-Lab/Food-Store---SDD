# Contribuyendo al Frontend de Food Store

Gracias por querer contribuir a Food Store. Este documento te guía en los procesos y estándares del proyecto.

---

## Antes de empezar

Lee estos archivos en `frontend/`:
1. `README.md` — Setup y scripts
2. `COMPONENT_GUIDE.md` — Cómo crear componentes
3. `HTTP_CLIENT_GUIDE.md` — Cómo integrar con la API
4. `ROUTING_GUIDE.md` — Cómo agregar nuevas rutas

---

## Workflow

### 1. Branching

```bash
git checkout -b feature/nombre-descriptivo
```

Nombres de branches:
- `feature/agregar-login` — Nueva feature
- `bugfix/modal-no-cierra` — Bug fix
- `refactor/componentes-atomicos` — Refactoring
- `docs/readme` — Documentación

### 2. Commits

Usa **Conventional Commits**:

```bash
feat: agregar formulario de login
fix: corregir error al parsear token JWT
refactor: simplificar componente Button
docs: actualizar guía de componentes
test: agregar tests para AuthContext
chore: actualizar dependencias
```

### 3. Before Push

Antes de hacer push, ejecutá:

```bash
# 1. Lint
npm run lint

# 2. Auto-fix (si es necesario)
npm run lint:fix

# 3. Tests
npm run test

# 4. Build
npm run build
```

Si alguno de estos falla, corregí el código antes de pushear.

### 4. Pull Request

Al hacer PR, incluí:
- **Descripción**: Qué cambios hace el PR
- **Why**: Por qué fueron necesarios
- **Testing**: Cómo testeaste

Ejemplo:

```markdown
## Descripción
Agrego validación en el formulario de login para verificar email antes de enviar.

## Why
Los tests fallaban porque emails inválidos llegaban a la API.

## Testing
- Agregué tests en LoginForm.test.tsx
- Testeé manualmente: validación funciona con emails inválidos
- npm run test pasa en 100%
```

---

## Estándares de código

### TypeScript

- Siempre usá tipos explícitos
- No usés `any`
- Usa `unknown` si realmente no sabés el tipo

```typescript
// ✅ Correcto
const parseUser = (data: unknown): User => {
  if (typeof data === 'object' && data !== null && 'id' in data) {
    return data as User;
  }
  throw new Error('Invalid user data');
};

// ❌ Evitá
const parseUser = (data: any): any => {
  return data as User;
};
```

### Componentes

- **Functional components** con `React.FC`
- **JSDoc comments** para documentar props
- **Props interface** explícita
- **Nombres descriptivos**

```typescript
interface CardProps {
  /** Título de la tarjeta */
  title?: string;
  /** Contenido de la tarjeta */
  children: React.ReactNode;
  /** Clases CSS adicionales */
  className?: string;
}

/**
 * Card component
 * Contenedor con padding y shadow
 */
export const Card: React.FC<CardProps> = ({ title, children, className }) => {
  return (
    <div className={`card ${className}`}>
      {title && <h2 className="card__title">{title}</h2>}
      <div className="card__content">{children}</div>
    </div>
  );
};
```

### Estilos

- Usa BEM naming para clases CSS: `componente__elemento--modificador`
- CSS modules o styled-components (discutí con el equipo)
- No hardcodees colores/tamaños; usá variables CSS

```css
/* ✅ Correcto */
.button {
  padding: var(--spacing-md);
  background-color: var(--color-primary);
  border-radius: var(--border-radius);
}

.button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ❌ Evitá */
.button {
  padding: 12px;
  background-color: #007bff;
}
```

### Hooks personalizados

- Comienza con `use`
- Documenta qué hace en JSDoc
- Retorna valores/funciones en orden lógico

```typescript
/**
 * Hook para cargar clientes
 * @returns { clientes, isLoading, error, reload }
 */
export const useClienteList = () => {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = async () => {
    setIsLoading(true);
    try {
      const response = await ClienteService.listClientes();
      setClientes(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  return { clientes, isLoading, error, reload };
};
```

---

## Testing

### Coverage goal: 80%

```bash
npm run test -- --coverage
```

Escribí tests para:
- Componentes nuevos
- Lógica crítica en hooks
- Funciones de utilidad

### Ejemplo

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  test('renders email and password inputs', () => {
    render(<LoginForm onSubmit={vi.fn()} />);
    
    expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
  });

  test('submits form with valid email and password', async () => {
    const handleSubmit = vi.fn();
    render(<LoginForm onSubmit={handleSubmit} />);
    
    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(emailInput, 'user@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'password123',
    });
  });

  test('shows error for invalid email', async () => {
    render(<LoginForm onSubmit={vi.fn()} />);
    
    const emailInput = screen.getByPlaceholderText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');
    
    // Trigger blur o form submit
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
  });
});
```

---

## Review checklist

Antes de hacer PR, verifica:

- [ ] Lint pasa (`npm run lint`)
- [ ] Tests pasan (`npm run test`)
- [ ] Build es exitoso (`npm run build`)
- [ ] Seguí Conventional Commits
- [ ] Agregué tests para cambios nuevos
- [ ] Documentación está actualizada
- [ ] Nada hardcodeado (colors, sizes, URLs)
- [ ] Props interfaces documentadas
- [ ] JSDoc comments en funciones/hooks

---

## Questions?

- Abrí una issue en GitHub
- Preguntá en Discord o Slack del equipo

---

Gracias por contribuir! 🚀
