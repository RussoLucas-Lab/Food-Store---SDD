# Component Guide

How to create and use Atoms, Molecules, and Organisms in Food Store frontend.

## Atoms (Basic Building Blocks)

Atoms are the smallest, most reusable components. They have no business logic.

### Button Component

```typescript
// src/shared/components/atoms/Button.tsx
import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

/**
 * Button atom: primary action component
 * @param variant - Style variant
 * @param size - Button size
 * @param disabled - Disable button
 * @param children - Button label
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
  children,
}) => {
  const classes = `btn btn-${variant} btn-${size} ${disabled ? 'disabled' : ''}`;
  return (
    <button className={classes} disabled={disabled} onClick={onClick}>
      {children}
    </button>
  );
};
```

### Input Component

```typescript
// src/shared/components/atoms/Input.tsx
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  name?: string;
}

export const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  name,
}) => {
  return (
    <div className="input-group">
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        name={name}
        className={error ? 'error' : ''}
      />
      {error && <span className="error-text">{error}</span>}
    </div>
  );
};
```

## Molecules (Combinations of Atoms)

Molecules combine atoms to create meaningful units. They handle simple presentation logic.

### FormField Molecule

```typescript
// src/shared/components/molecules/FormField.tsx
import React from 'react';
import { Label } from '../atoms/Label';
import { Input } from '../atoms/Input';

interface FormFieldProps {
  label: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  required?: boolean;
}

/**
 * FormField molecule: combines Label + Input
 */
export const FormField: React.FC<FormFieldProps> = ({
  label,
  type,
  placeholder,
  value,
  onChange,
  error,
  required,
}) => {
  return (
    <div className="form-field">
      <Label required={required}>{label}</Label>
      <Input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        error={error}
      />
    </div>
  );
};
```

### Card Molecule

```typescript
// src/shared/components/molecules/Card.tsx
interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * Card molecule: container with optional title
 */
export const Card: React.FC<CardProps> = ({ title, children, className }) => {
  return (
    <div className={`card ${className || ''}`}>
      {title && <div className="card-header">{title}</div>}
      <div className="card-body">{children}</div>
    </div>
  );
};
```

## Organisms (Complex Components)

Organisms are complex, feature-rich components. They often include business logic and multiple molecules/atoms.

### Header Organism

```typescript
// src/shared/components/organisms/Header.tsx
import React from 'react';
import { useAuth } from '@/shared/context';
import { useTheme } from '@/shared/context';
import { Button } from '../atoms/Button';

/**
 * Header organism: main navigation and user menu
 */
export const Header: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="header">
      <div className="header-left">
        <h1>Food Store</h1>
        {isAuthenticated && (
          <nav>
            <a href="/productos">Productos</a>
            <a href="/clientes">Clientes</a>
          </nav>
        )}
      </div>

      <div className="header-right">
        <button onClick={toggleTheme} className="theme-toggle">
          {theme === 'light' ? '🌙' : '☀️'}
        </button>

        {isAuthenticated ? (
          <>
            <span>Hola, {user?.nombre}</span>
            <Button variant="danger" onClick={logout}>
              Logout
            </Button>
          </>
        ) : (
          <Button onClick={() => (window.location.href = '/login')}>
            Login
          </Button>
        )}
      </div>
    </header>
  );
};
```

### Layout Organism

```typescript
// src/shared/components/organisms/Layout.tsx
/**
 * Layout organism: wraps page with Header, Sidebar, and Footer
 */
export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="layout">
      <Header />
      <div className="layout-body">
        <Sidebar />
        <main className="main-content">{children}</main>
      </div>
      <Footer />
    </div>
  );
};
```

## Creating New Components

### 1. Decide the Level

- **Atom**: No dependencies on other components, pure presentation
- **Molecule**: Combines atoms, handles presentation logic
- **Organism**: Complex, may include API calls or routing

### 2. Create the Component

```typescript
// src/shared/components/atoms/YourComponent.tsx
import React from 'react';

interface YourComponentProps {
  prop1: string;
  prop2?: number;
  children?: React.ReactNode;
}

/**
 * YourComponent: brief description
 * @param prop1 - Description
 * @param prop2 - Description
 */
export const YourComponent: React.FC<YourComponentProps> = ({
  prop1,
  prop2,
  children,
}) => {
  return <div>{/* JSX here */}</div>;
};
```

### 3. Export from Barrel

```typescript
// src/shared/components/atoms/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { YourComponent } from './YourComponent';
```

### 4. Use in Other Components

```typescript
import { Button, Input, YourComponent } from '@/shared/components/atoms';

export const MyPage = () => {
  return (
    <>
      <YourComponent prop1="test" />
      <Button>Click</Button>
    </>
  );
};
```

## Best Practices

1. **Keep atoms simple** - No context, no hooks beyond useState
2. **Document with JSDoc** - Include @param descriptions
3. **Use TypeScript** - Define all props with interfaces
4. **One responsibility** - Each component has one purpose
5. **Reuse over copy-paste** - Extract common patterns
6. **Test as you build** - Add tests for new components
7. **Export from barrels** - Always use index.ts files
