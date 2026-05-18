## Why

El panel de administración tiene un único stub `CatalogoAdminPage` que solo carga categorías sin edición, y deja ingredientes y productos completamente sin gestión visual. Los administradores y gestores de stock necesitan dashboards completos de ABM para operar el catálogo sin tocar la consola ni Swagger.

## What Changes

- **Reemplazar** `CatalogoAdminPage` (stub) por tres páginas CRUD independientes accesibles desde el admin panel.
- **Crear** `CategoriasAdminPage` con tabla paginada + modal crear/editar + confirmación de eliminación.
- **Crear** `IngredientesAdminPage` con tabla paginada + modal crear/editar (incluye unidad de medida, stock, cantidad mínima, categoría asociada) + confirmación de eliminación.
- **Crear** `ProductosAdminPage` con tabla paginada + modal crear/editar (precio, categorías M2M, ingredientes con cantidad requerida) + confirmación de eliminación.
- **Crear** servicios y hooks de TanStack Query v5 para las tres entidades.
- **Actualizar** `AdminNav` para incluir los tres nuevos links bajo la sección Catálogo.
- **Actualizar** `router.tsx` con tres nuevas rutas bajo `/admin`.
- Todos los endpoints CRUD del backend ya existen — no se crea código backend nuevo.

## Capabilities

### New Capabilities

- `admin-catalogo-crud`: ABM completo de Categorías, Ingredientes y Productos desde el panel de administración, consumiendo los endpoints REST existentes del backend.

### Modified Capabilities

- `admin-panel-frontend`: Se añaden tres rutas y tres entradas de navegación para los nuevos dashboards CRUD (Categorías, Ingredientes, Productos), accesibles para ADMIN y STOCK.

## Impact

- **Frontend — nuevos archivos**: 3 páginas (`CategoriasAdminPage`, `IngredientesAdminPage`, `ProductosAdminPage`), 3 servicios API (`adminCategoriasApi`, `adminIngredientesApi`, `adminProductosApi`), 3 hooks TanStack Query (`useCategorias`, `useIngredientes`, `useProductosAdmin`).
- **Frontend — archivos modificados**: `router.tsx`, `AdminNav.tsx`, `features/admin/pages/index.ts`, `features/admin/services/index.ts`, `features/admin/hooks/index.ts`.
- **Frontend — eliminado**: `CatalogoAdminPage.tsx` (stub reemplazado).
- **Backend**: sin cambios — todos los endpoints necesarios existen y están protegidos por `require_role("admin", "ADMIN", "stock", "STOCK")`.
- **Dependencias**: ninguna nueva — TanStack Query v5 y Tailwind CSS 3 ya están instalados.
