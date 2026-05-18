## Why

El proyecto tiene toda la lógica de backend, checkout y admin implementada, pero el flujo de compra del cliente (catálogo, detalle de producto, carrito) nunca fue construido en el frontend — las páginas de productos son stubs vacíos, no existe CartDrawer, y el uiStore requerido por la arquitectura está ausente. Sin esto, el e-commerce no es funcional desde la perspectiva del cliente.

## What Changes

- **Nueva `CatalogoPage`** (`/productos`): listado de productos con búsqueda por nombre, filtro por categoría, paginación y tarjetas de producto.
- **Nueva `ProductoDetailPage`** (`/productos/:id`): detalle del producto con selección de ingredientes a excluir y botón "Agregar al carrito".
- **Nuevo `CartDrawer`**: panel lateral deslizable que muestra los ítems del carrito, permite ajustar cantidades/eliminar, y tiene CTA hacia `/checkout`.
- **Nueva `HomePage`** (`/`): landing page con hero y acceso directo al catálogo (reemplaza el placeholder actual).
- **Nuevo `uiStore`**: store Zustand no persistido que gestiona `cartOpen`, `sidebarOpen` y `confirmModal`; requerido por la arquitectura (CE-11).
- **`PedidoConfirmacionPage` real**: página con estado del pedido, link a `/mis-pedidos`, y resumen básico (reemplaza el placeholder actual).
- **UX transversal**: estados de carga (skeleton loaders), estados vacíos con CTAs, feedback de errores/éxito (toast), y responsive mobile básico en páginas nuevas.

## Capabilities

### New Capabilities
- `catalogo-tienda`: Páginas del catálogo cliente — listado de productos, detalle, búsqueda/filtro por categoría e integración con el carrito (CartDrawer).
- `ui-experiencia-cliente`: UX base transversal — uiStore, loading states, empty states, toast notifications, y responsive layout.

### Modified Capabilities
<!-- Ninguna. Los cambios son additive: páginas nuevas y un store nuevo. Las specs existentes no cambian de requerimientos. -->

## Impact

- `frontend/src/features/productos/` — implementación completa (pages, hooks, services, components)
- `frontend/src/shared/stores/uiStore.ts` — nuevo store Zustand (no persistido)
- `frontend/src/shared/components/` — nuevos atoms/molecules: CartDrawer, SkeletonCard, Toast
- `frontend/src/router.tsx` — reemplazar stubs HomePage, ProductosLayout y PedidoConfirmacionPage
- Sin cambios en el backend ni en specs de otros módulos
