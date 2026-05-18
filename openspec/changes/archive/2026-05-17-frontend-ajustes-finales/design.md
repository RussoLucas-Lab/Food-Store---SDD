## Context

El frontend de Food Store tiene implementadas las features de auth, admin, clientes, pedidos y pagos, pero la feature `productos/` es un esqueleto vacío (solo `index.ts` con placeholders). El router.tsx tiene `ProductosLayout`, `HomePage` y `PedidoConfirmacionPage` como stubs inline. El uiStore está ausente aunque es requerido por CE-11. El cartStore ya existe y funciona; el CartDrawer que lo consume no existe.

El stack frontend es React 18 + TypeScript + Vite + TanStack Query v5 + Tailwind CSS 3. El patrón es Feature-Sliced Design: cada feature tiene `pages/`, `hooks/`, `services/`, `components/`.

## Goals / Non-Goals

**Goals:**
- Implementar la feature `productos/` completa: CatalogoPage, ProductoDetailPage, hooks y services para productos y categorías.
- Crear el CartDrawer como componente compartido controlado por uiStore.
- Crear uiStore con `cartOpen`, `sidebarOpen`, `confirmModal`.
- Reemplazar stubs HomePage y PedidoConfirmacionPage con páginas funcionales.
- UX básica: skeleton loaders, empty states, toast simple (sin librería externa).

**Non-Goals:**
- Tests e2e (son change 13 — pruebas-integracion).
- Integración MercadoPago frontend (ya implementada en pago-gestion).
- Paginación server-side avanzada (basta con `?page=1&size=20` básico).
- i18n o internacionalización.
- Animaciones complejas o micro-interactions avanzadas.

## Decisions

### D1 — Feature `productos/` sigue el mismo patrón que `clientes/`
Cada feature tiene `services/api.ts` (Axios hacia `/api/v1/...`), `hooks/useProductos.ts` (TanStack Query), `components/` y `pages/`. Alternativa: mover catálogo a `store/` feature separada. Rechazada — introduce una feature nueva sin justificación; `productos/` ya existe y es el lugar correcto.

### D2 — CartDrawer vive en `shared/components/organisms/`
El CartDrawer consume el cartStore (shared) y el uiStore (shared), y es invocable desde cualquier página. Alternativa: ponerlo en `productos/` o `pedidos/`. Rechazada — el cart es transversal, no pertenece a una feature.

### D3 — uiStore como módulo singleton (mismo patrón que cartStore)
Se usa `useSyncExternalStore` en lugar de Zustand para mantener consistencia con la implementación actual del cartStore. No requiere dependencia adicional.

### D4 — Toast sin librería externa
Se implementa un `ToastContainer` simple con `useToast` hook usando `useSyncExternalStore` o Context. Alternativa: `react-hot-toast` o `sonner`. Rechazada por ahora para no agregar dependencias; si el resultado es insuficiente se puede reemplazar en pruebas-integracion.

### D5 — Catálogo público sin auth
`GET /api/v1/productos` y `GET /api/v1/categorias` son endpoints públicos (RN-CA08, RN-RB10). La CatalogoPage no requiere login para browsear. El botón "Agregar al carrito" está disponible sin login (el carrito es client-side); el checkout sí requiere auth.

### D6 — ProductoDetailPage usa la misma URL que el router actual: `/productos/:id`
El router tiene `<Route path="/productos/*" element={<ProductosLayout />} />`. Se reemplaza con rutas específicas: `/productos` para catálogo y `/productos/:id` para detalle.

## Risks / Trade-offs

- **API backend en modo in-memory**: el backend usa repos in-memory (no PostgreSQL todavía). Los endpoints de productos/categorías devuelven los datos seed. Mitigation: las páginas frontend funcionan igual; si el seed no tiene datos, los estados vacíos lo manejan.
- **CartDrawer y re-renders**: si el uiStore notifica a todos los suscriptores en cada toggle, puede causar re-renders innecesarios. Mitigation: usar selectores granulares igual que cartStore.
- **Responsive mobile**: Tailwind facilita mobile-first pero sin diseño UX previo puede quedar inconsistente. Mitigation: scope acotado — mobile básico (flex-col en mobile, grid en desktop) es suficiente para esta entrega.

## Migration Plan

1. Crear `uiStore.ts` en shared/stores (sin romper nada existente).
2. Implementar feature `productos/` completa (pages, hooks, services, components).
3. Agregar CartDrawer a `shared/components/organisms/`.
4. Actualizar router.tsx: reemplazar stubs, agregar rutas `/productos` y `/productos/:id`.
5. Conectar CartDrawer al Layout existente.
6. Verificar que rutas existentes (checkout, admin, pedidos) no se rompan.

No hay rollback plan necesario — todos los cambios son additive excepto el reemplazo de stubs en router.tsx.
