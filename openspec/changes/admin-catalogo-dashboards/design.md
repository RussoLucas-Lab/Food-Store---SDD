## Context

El panel de administración (`/admin/*`) ya existe con `AdminLayout`, `AdminNav` y cinco páginas. La página `CatalogoAdminPage` es un stub que solo lista categorías con llamadas axios crudas (sin TanStack Query, sin edición, sin ingredientes ni productos). Los tres routers FastAPI para categorías, ingredientes y productos están completos con endpoints CRUD protegidos por rol ADMIN/STOCK.

El stack frontend usa React 18, TanStack Query v5, Tailwind CSS 3 y axios. La skill `dashboard-crud-page` referenciada por el usuario pertenece a otro proyecto y sus hooks (`useFormModal`, `useConfirmDialog`, `usePagination`) y componentes (`PageContainer`, `HelpButton`, `Modal`) no existen en FoodStore — los patrones de la skill se adaptan usando primitivas disponibles.

## Goals / Non-Goals

**Goals:**
- Tres páginas CRUD independientes para Categorías, Ingredientes y Productos en el admin panel.
- Cada página: tabla paginada del lado del cliente, modal crear/editar, confirmación de eliminación.
- Servicios y hooks TanStack Query v5 por dominio (separación service/hook).
- Formularios controlados con validación en el cliente antes de llamar a la API.
- Feedback visual: loading skeleton en tabla, toast de éxito/error, badge de estado activo/inactivo.
- Rutas nuevas: `/admin/categorias`, `/admin/ingredientes`, `/admin/productos`.
- Nav actualizado: tres links bajo la sección Catálogo (visibles para ADMIN y STOCK).

**Non-Goals:**
- No se crea código backend nuevo.
- No se implementa paginación server-side (el backend soporta `skip`/`limit`, pero el volumen académico no lo requiere — se trae todo y se pagina en cliente).
- No se gestiona soft-delete (la API hace DELETE con soft delete internamente; el frontend solo llama al endpoint).
- No se implementa upload de imágenes para productos.
- No se crea el árbol de categorías jerárquico (el backend tiene padre_id, pero la UI solo muestra lista plana).

## Decisions

### D1 — Una página por entidad (3 rutas separadas) en lugar de tabs en una sola página

La propuesta pide "tres dashboards distintos". Cada uno vive en su propia ruta (`/admin/categorias`, `/admin/ingredientes`, `/admin/productos`), con su propio archivo `.tsx`, servicio y hook.  
**Alternativa descartada**: tabs dentro de `CatalogoAdminPage` → más difícil de navegar, más difícil de mantener, mezcla hooks de distintos dominios.

### D2 — TanStack Query v5 para state del servidor (no useState + axios manual)

Se crean hooks `useCategorias()`, `useIngredientes()`, `useProductosAdmin()` que encapsulan `useQuery` + `useMutation` + `queryClient.invalidateQueries`. El estado de loading/error viene del hook.  
**Alternativa descartada**: axios + useState como el stub actual → no cachea, no invalida, no maneja error/loading de forma uniforme.

### D3 — Modal nativo con estado local (useState) en lugar de un hook reutilizable

La skill `dashboard-crud-page` prescribe `useFormModal<F,E>`. Como ese hook no existe en FoodStore, cada página tiene su propio `modalOpen`, `editingItem`, `formData` como `useState` local. La lógica es simple y no justifica crear el hook compartido en este change.  
**Alternativa considerada**: crear `useFormModal` como hook compartido en `shared/hooks/` → overkill para 3 páginas en un TPI; se puede hacer en un change posterior si el proyecto escala.

### D4 — Paginación en cliente con slice manual

Cada hook trae los items con `limit=100`. El componente pagina con `useMemo` sobre el array local (`items.slice((page-1)*PAGE_SIZE, page*PAGE_SIZE)`).  
**Alternativa descartada**: server-side pagination con `skip`/`limit` en cada cambio de página → complejidad innecesaria para volúmenes académicos (< 50 registros).

### D5 — Formulario de Producto con selección múltiple de categorías e ingredientes

El backend exige `categories: int[]` (mín 1) e `ingredients: [{ingredient_id, quantity_required}]` (mín 1). El modal de producto incluye:
- checkboxes para categorías (cargadas con `useCategorias`)
- tabla dinámica de ingredientes con campo de cantidad (cargados con `useIngredientes`)

Esto hace el modal de productos más complejo que los otros dos, pero es imprescindible para el endpoint `POST /api/v1/productos`.

### D6 — Estructura de archivos dentro de `features/admin/`

```
features/admin/
├── pages/
│   ├── CategoriasAdminPage.tsx     (nuevo)
│   ├── IngredientesAdminPage.tsx   (nuevo)
│   ├── ProductosAdminPage.tsx      (nuevo)
│   └── CatalogoAdminPage.tsx       (ELIMINADO — reemplazado)
├── services/
│   ├── adminCategoriasApi.ts       (nuevo)
│   ├── adminIngredientesApi.ts     (nuevo)
│   └── adminProductosApi.ts        (nuevo)
└── hooks/
    ├── useCategorias.ts            (nuevo)
    ├── useIngredientes.ts          (nuevo)
    └── useProductosAdmin.ts        (nuevo)
```

### D7 — Confirmación de eliminación con dialog nativo del navegador (window.confirm)

Para no crear un componente `ConfirmDialog` desde cero, la eliminación usa `window.confirm()`. Patrón simple, suficiente para un TPI académico.  
**Alternativa considerada**: modal de confirmación Tailwind → mejor UX pero agrega ~50 líneas de boilerplate por página sin valor académico adicional.

### D8 — Toast de feedback con un componente inline simple

No existe una librería de toasts ni un componente `Toast` global en FoodStore. Se usa un estado `toast: { message, type } | null` con `setTimeout` para auto-cerrar. Se muestra como un `div` flotante con Tailwind (fijo, arriba a la derecha).

## Risks / Trade-offs

- **Modal de Producto complejo** → la selección de ingredientes con cantidades (tabla dinámica) es la parte más propensa a bugs. Mitigación: validar en el cliente que al menos 1 ingrediente con `quantity_required > 0` antes de llamar a la API.
- **`window.confirm` accesibilidad** → no es ideal pero es suficiente en contexto académico. Mitigación: texto descriptivo en el mensaje de confirmación.
- **Sin test coverage nuevo** → las páginas nuevas no tienen tests unitarios en este change (cobertura ya cumplida en change `pruebas-integracion`). Mitigación: el backend está cubierto; las páginas admin son UI thin wrappers.
- **`CatalogoAdminPage` eliminada** → la ruta `/admin/catalogo` queda obsoleta. Mitigación: agregar redirect `/admin/catalogo` → `/admin/categorias` en el router para no romper bookmarks existentes.

## Migration Plan

1. Instalar: sin dependencias nuevas.
2. Crear servicios y hooks (sin efecto en UI).
3. Crear las 3 páginas nuevas.
4. Actualizar `router.tsx`: agregar 3 rutas nuevas + redirect `/admin/catalogo` → `/admin/categorias`.
5. Actualizar `AdminNav.tsx`: reemplazar link "Catálogo" por tres links individuales.
6. Eliminar `CatalogoAdminPage.tsx`.
7. Actualizar barrel exports (`index.ts`).

**Rollback**: revertir los archivos modificados; `CatalogoAdminPage` puede recuperarse desde git.

## Open Questions

- *(resuelto)* ¿Un change o tres? → Un solo change cubre los tres dashboards.
- *(resuelto)* ¿Crear `useFormModal` compartido? → No en este change; estado local por página.
- ¿El campo `disponible` de Producto debe editarse directamente desde la tabla (toggle inline) o solo desde el modal? → **Decisión: solo desde el modal** (menos complejidad).
