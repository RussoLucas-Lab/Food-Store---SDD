## 1. uiStore — Store global de UI

- [x] 1.1 Crear `frontend/src/shared/stores/uiStore.ts` con estado `cartOpen`, `sidebarOpen`, `confirmModal` (no persistido, patrón `useSyncExternalStore` igual que cartStore)
- [x] 1.2 Exportar `useUiStore` hook con selector obligatorio
- [x] 1.3 Agregar export de `uiStore` en `frontend/src/shared/stores/index.ts` (o crear el index si no existe)

## 2. Toast — Notificaciones de feedback

- [x] 2.1 Crear `frontend/src/shared/hooks/useToast.ts` — hook con `showToast(message, type)` y lista de toasts activos
- [x] 2.2 Crear `frontend/src/shared/components/atoms/Toast.tsx` — componente individual de toast (verde/rojo/neutro)
- [x] 2.3 Crear `frontend/src/shared/components/organisms/ToastContainer.tsx` — renderiza la lista de toasts activos, posición fixed bottom-right
- [x] 2.4 Integrar `ToastContainer` en el Layout principal (`frontend/src/shared/components/organisms/Layout.tsx`)

## 3. Skeleton loaders

- [x] 3.1 Crear `frontend/src/shared/components/atoms/SkeletonCard.tsx` — tarjeta gris animada con pulse para placeholder de productos
- [x] 3.2 Crear `frontend/src/shared/components/atoms/SkeletonDetail.tsx` — skeleton para el layout de detalle de producto

## 4. Productos — Services y hooks

- [x] 4.1 Crear `frontend/src/features/productos/services/productosApi.ts` — funciones `getProductos(params)` y `getProductoById(id)` usando Axios hacia `GET /api/v1/productos` y `GET /api/v1/productos/:id`
- [x] 4.2 Crear `frontend/src/features/productos/services/categoriasApi.ts` — función `getCategorias()` hacia `GET /api/v1/categorias`
- [x] 4.3 Actualizar `frontend/src/features/productos/services/index.ts` con los exports
- [x] 4.4 Crear `frontend/src/features/productos/hooks/useProductos.ts` — TanStack Query hook con filtro por categoría y búsqueda por nombre
- [x] 4.5 Crear `frontend/src/features/productos/hooks/useProducto.ts` — TanStack Query hook para `GET /api/v1/productos/:id`
- [x] 4.6 Crear `frontend/src/features/productos/hooks/useCategorias.ts` — TanStack Query hook para listado de categorías
- [x] 4.7 Actualizar `frontend/src/features/productos/hooks/index.ts` con los exports

## 5. Productos — Componentes

- [x] 5.1 Crear `frontend/src/features/productos/components/ProductoCard.tsx` — tarjeta con nombre, precio, imagen placeholder y botón "Agregar" que invoca `cartStore.addItem`
- [x] 5.2 Crear `frontend/src/features/productos/components/ProductoGrid.tsx` — grilla responsiva de `ProductoCard` (3 cols desktop, 1 col mobile); muestra skeletons en loading, empty state si no hay datos
- [x] 5.3 Crear `frontend/src/features/productos/components/CatalogoFilters.tsx` — selector de categoría + input de búsqueda; estado local con debounce de 300ms
- [x] 5.4 Crear `frontend/src/features/productos/components/IngredienteSelector.tsx` — lista de ingredientes con checkboxes; deshabilita `es_removible=false`
- [x] 5.5 Actualizar `frontend/src/features/productos/components/index.ts` con los exports

## 6. Productos — Páginas

- [x] 6.1 Crear `frontend/src/features/productos/pages/CatalogoPage.tsx` — compone `CatalogoFilters` + `ProductoGrid`; maneja estado de filtros
- [x] 6.2 Crear `frontend/src/features/productos/pages/ProductoDetailPage.tsx` — muestra detalle del producto, `IngredienteSelector`, selector de cantidad y botón "Agregar al carrito"; skeleton en loading; error state si no encontrado
- [x] 6.3 Actualizar `frontend/src/features/productos/pages/index.ts` con los exports

## 7. CartDrawer

- [x] 7.1 Crear `frontend/src/shared/components/organisms/CartDrawer.tsx` — panel lateral: lista de ítems, controles de cantidad (+ / −), botón eliminar, total, CTA "Ir al checkout"; empty state si carrito vacío
- [x] 7.2 Conectar `CartDrawer` al `uiStore.cartOpen` para abrir/cerrar
- [x] 7.3 Integrar `CartDrawer` en el Layout principal (se renderiza siempre, visible/oculto según `cartOpen`)
- [x] 7.4 Actualizar el ícono de carrito en el header para que haga `setCartOpen(true)` y muestre el badge de cantidad

## 8. Router — Reemplazar stubs y agregar rutas

- [x] 8.1 En `frontend/src/router.tsx`: importar `CatalogoPage` y `ProductoDetailPage` desde `features/productos/pages`
- [x] 8.2 Reemplazar `<Route path="/productos/*" element={<ProductosLayout />} />` con rutas explícitas: `/productos` → `CatalogoPage`, `/productos/:id` → `ProductoDetailPage`
- [x] 8.3 Reemplazar el stub `HomePage` inline con un componente `HomePage` real (hero + CTA "Ver catálogo" → `/productos`)
- [x] 8.4 Reemplazar el stub `PedidoConfirmacionPage` con una página real que muestre ID del pedido, estado PENDIENTE, y links a `/mis-pedidos` y `/productos`
- [x] 8.5 Redirigir `/profile` a `/perfil` (eliminar la ruta duplicada con el stub `ProfilePage`)

## 9. Empty states en páginas existentes

- [x] 9.1 En `MisPedidosPage`: agregar empty state "Todavía no hiciste ningún pedido" con CTA "Ver catálogo" cuando la lista de pedidos está vacía
- [x] 9.2 En `CheckoutPage`: verificar que el link "Ir al catálogo" apunta a `/productos` (ya debería existir)

## 10. Integración final y verificación

- [x] 10.1 Ejecutar `npm run build` en el frontend — debe compilar sin errores TypeScript
- [x] 10.2 Verificar flujo completo: `/` → `/productos` → `/productos/:id` → agregar al carrito → abrir CartDrawer → `/checkout`
- [x] 10.3 Verificar responsive en Chrome DevTools con viewport 375px (mobile)
- [x] 10.4 Verificar que las rutas existentes no se rompieron: `/login`, `/register`, `/admin`, `/checkout`, `/mis-pedidos`, `/gestion/pedidos`
