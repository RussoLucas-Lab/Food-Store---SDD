"""
# Cliente Frontend Components Documentation

## Overview
Componentes React para la gestión de clientes en Food Store.
Implementan patrón Container-Presentational con custom hooks para state management.

## Components

### ClienteList
**Descripción**: Tabla/lista de clientes activos con acciones CRUD

**Props**:
- `clientes: Cliente[]` - Array de clientes a mostrar
- `isLoading: boolean` - Estado de carga
- `error: string | null` - Mensaje de error (si existe)
- `onDelete: (id: string) => void` - Callback para eliminar
- `onEdit: (cliente: Cliente) => void` - Callback para editar
- `onView: (id: string) => void` - Callback para ver detalles

**Comportamiento**:
- Muestra tabla responsive
- ADMIN ve: View, Edit, Delete buttons
- USER ve: solo View button
- Estados activos se marcan en verde, inactivos en rojo
- Validación: no hay clientes inactivos en esta vista

**Ejemplo**:
```tsx
<ClienteList
  clientes={clientes}
  isLoading={isLoading}
  error={error}
  onDelete={handleDelete}
  onEdit={handleEdit}
  onView={handleView}
/>
```

---

### ClienteForm
**Descripción**: Formulario reutilizable para crear/editar clientes

**Props**:
- `cliente?: Cliente | null` - Cliente a editar (omitir para create)
- `isLoading: boolean` - Estado de carga inicial
- `isSubmitting: boolean` - Estado durante submit
- `error: string | null` - Error general del formulario
- `onSubmit: (data: ClienteCreate | ClienteUpdate) => void` - Handler de submit
- `onCancel: () => void` - Handler de cancelación

**Validación**:
- Email: required, valid format (regex)
- Nombre: required, min 3 chars
- Teléfono: required, min 10 chars
- Dirección: required, no empty

**Comportamiento**:
- En modo CREATE: envía ClienteCreate
- En modo EDIT: envía ClienteUpdate (partial)
- Limpia errores de validación mientras el user tipea
- Button text cambia: "Crear cliente" vs "Guardar cambios"

**Ejemplo**:
```tsx
<ClienteForm
  cliente={selectedCliente}
  isSubmitting={isSubmitting}
  error={formError}
  onSubmit={handleSaveCliente}
  onCancel={handleCancel}
/>
```

---

### ClienteDetail
**Descripción**: Vista de detalles de un cliente con opciones de editar/eliminar

**Props**:
- `cliente: Cliente` - Cliente a mostrar
- `isLoading: boolean` - Estado de carga
- `error: string | null` - Mensaje de error
- `onEdit: () => void` - Callback para editar
- `onDelete: () => void` - Callback para eliminar
- `onBack: () => void` - Callback para volver
- `isOwnProfile?: boolean` - Si es el perfil del usuario actual

**Comportamiento**:
- Muestra todos los campos del cliente
- ADMIN ve: Edit, Delete buttons
- USER ve: Edit button (solo en perfil propio)
- USER nunca ve Delete button
- Estado soft-delete se muestra claramente
- Fechas en formato local (es-AR)

**Ejemplo**:
```tsx
<ClienteDetail
  cliente={cliente}
  isLoading={isLoading}
  error={error}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onBack={handleBack}
  isOwnProfile={true}
/>
```

---

### ClienteSearch
**Descripción**: Barra de búsqueda debounced para filtrar clientes

**Props**:
- `onSearch: (query: string) => void` - Callback cuando búsqueda cambia
- `isLoading?: boolean` - Estado de carga (default: false)
- `placeholder?: string` - Placeholder del input (default: "Buscar por nombre o email...")
- `debounceMs?: number` - Delay antes de disparar búsqueda (default: 300)

**Comportamiento**:
- Debounced input: espera 300ms sin cambios antes de llamar onSearch
- Clear button (✕) aparece cuando hay texto
- Admin-only: solo visible para ADMIN
- Búsqueda por nombre O email (OR logic)

**Ejemplo**:
```tsx
<ClienteSearch
  onSearch={handleSearch}
  isLoading={isSearching}
  debounceMs={500}
/>
```

---

## Custom Hooks

### useClienteForm
**Descripción**: Manage form state (loading, error, submitting)

**Returns**:
```typescript
{
  isLoading: boolean;
  error: string | null;
  isSubmitting: boolean;
  setFormLoading: (loading: boolean) => void;
  setFormError: (err: string | null) => void;
  setFormSubmitting: (submitting: boolean) => void;
  clearError: () => void;
  resetForm: () => void;
}
```

**Uso**:
```tsx
const formState = useClienteForm();
// ... use formState.setFormSubmitting(), formState.setFormError(), etc.
```

---

### useClienteList
**Descripción**: Manage list state (loading, error, items, pagination)

**Returns**:
```typescript
{
  isLoading: boolean;
  error: string | null;
  items: Cliente[];
  total: number;
  page: number;
  limit: number;
  setListLoading: (loading: boolean) => void;
  setListError: (err: string | null) => void;
  setListItems: (items: Cliente[]) => void;
  setListPagination: (page: number, limit: number, total: number) => void;
  clearError: () => void;
  resetList: () => void;
}
```

**Uso**:
```tsx
const listState = useClienteList();
// ... use listState.setListItems(), listState.setListLoading(), etc.
```

---

## Pages

### ClientesPage
URL: `/clientes`
- Admin: lista todos los clientes activos
- User: ve solo su perfil (si existe)
- Search: solo admin puede buscar
- Botón "Nuevo Cliente": solo admin

### ClienteCreatePage
URL: `/clientes/crear`
- Solo admin
- Formulario vacío para crear cliente
- Redirect a /clientes on success

### ClienteDetailPage
URL: `/clientes/:id` (view mode)
URL: `/clientes/:id/editar` (edit mode)
- Admin: ver/editar/eliminar cualquier cliente
- User: ver/editar solo propio perfil
- Toggle view ↔ edit mode

### PerfilPage
URL: `/perfil`
- Usuario ve su propio perfil
- Puede editar su información
- No puede eliminar su perfil
- Muestra mensaje si no tiene perfil creado

---

## Error Handling

### API Errors
Manejados por `ClienteService.catch()` → `handleApiError()`:
- 400: Validation error (email duplicate, format invalid, etc.)
- 401: Unauthorized (token expired, not authenticated)
- 403: Forbidden (user can't edit other's profile)
- 404: Not found (cliente doesn't exist)
- 409: Conflict (email already exists)
- 5xx: Server error

### Validation Errors
Mostrados en FormField:
- Email: format, required
- Name: length (3+), required
- Phone: length (10+), required
- Address: required

### Network Errors
Retry logic: 3 intentos con backoff exponencial
- 1st retry: +1s delay
- 2nd retry: +2s delay
- 3rd retry: +3s delay

---

## Authorization & Role-Based UI

### ADMIN
- Create, Read, List, Update, Delete all clientes
- View soft-deleted clientes (marked as inactive)
- Search clientes
- Reactivate clientes

### USER
- Read own profile
- Update own profile
- Cannot create, delete, or view other clientes

### GUEST
- No access (redirect to /login)

---

## Styling

All components use CSS modules with responsive design:
- Desktop: table layout
- Tablet: grid layout
- Mobile: stacked layout

Colors:
- Active: green (#d4edda text, #155724)
- Inactive: red (#f8d7da text, #721c24)
- Error: red (#dc3545)
- Success: green (#28a745)

---

## Example Workflow

1. **Admin creates cliente**:
   - Navigate to `/clientes`
   - Click "+ Nuevo Cliente"
   - Fill form → Submit
   - Redirect to `/clientes`
   - New cliente appears in list

2. **User edits own profile**:
   - Navigate to `/perfil`
   - Click "Editar"
   - Form switches to edit mode
   - Update fields → Submit
   - Profile updates in place

3. **Admin searches clientes**:
   - Navigate to `/clientes`
   - Type in search box (debounced)
   - List filters automatically
   - Clear button resets to full list

---

## Testing

See `conftest.py` for fixtures:
- `cliente_fixture`: single cliente instance
- `multiple_clientes_fixture`: list of clientes
- `admin_user_fixture`, `regular_user_fixture`: user roles
- `rbac_test_scenarios`: RBAC test cases
"""
