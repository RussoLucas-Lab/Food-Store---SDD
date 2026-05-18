# Proposal — direcciones-cliente

## Why

El cliente autenticado necesita administrar sus direcciones de entrega (alta, edición,
baja, marcado de predeterminada) y seleccionar una dirección al momento del checkout.

El backend ya expone el dominio completo en `backend/modules/direcciones/`
(router, service, repository, model, schemas) con 5 endpoints bajo
`/api/v1/clientes/me/direcciones`. En el frontend ya existen las piezas base:

- `direccionClient.ts` — cliente HTTP con los 5 métodos y tipos.
- `DireccionManager.tsx` — componente CRUD completo (lista, formulario crear/editar,
  eliminar, marcar predeterminada) con TanStack Query inline.
- `DirectionSelector.tsx` — selector de dirección para checkout, con pre-selección
  de la predeterminada.
- `CheckoutPage.tsx` — ya integra `DirectionSelector` + `CreateOrderButton`.

El cambio cierra los huecos que impiden que esa funcionalidad sea usable de punta a
punta: la página de perfil no monta el `DireccionManager`, no hay una ruta dedicada
para gestión de direcciones, y la lógica de servidor está duplicada inline en cada
componente en lugar de centralizada en hooks reutilizables (convención del proyecto:
`features/<dominio>/hooks/`).

## What Changes

1. **Hooks centralizados de direcciones** — extraer la lógica TanStack Query a
   `features/pedidos/hooks/useDirecciones.ts`: `useDirecciones`, `useCreateDireccion`,
   `useUpdateDireccion`, `useDeleteDireccion`, `useSetDireccionPredeterminada`.
   Una sola `queryKey` `['direcciones']` y una sola política de invalidación.
2. **Refactor de componentes existentes** — `DireccionManager` y `DirectionSelector`
   consumen los hooks en lugar de llamar a `direccionClient` y declarar mutations
   inline. No cambia el comportamiento visible.
3. **Integración en el perfil** — `PerfilPage` monta `DireccionManager` en una sección
   "Mis Direcciones", de modo que la gestión de direcciones sea alcanzable desde la UI.
4. **Ruta dedicada** — agregar `/perfil/direcciones` (protegida, CLIENT) que renderiza
   el `DireccionManager` como página independiente.
5. **Checkout consistente** — los enlaces "Agregar Nueva Dirección" de `DirectionSelector`
   apuntan a `/perfil/direcciones` y el `CheckoutPage` deja el `selectedDirectionId`
   listo para la creación del pedido (sin permitir continuar si no hay dirección).

## Impact

- Affected specs: `direcciones-frontend` (nuevo capability spec delta).
- Affected code (frontend, FSD):
  - Nuevo: `frontend/src/features/pedidos/hooks/useDirecciones.ts`
  - Nuevo: `frontend/src/features/pedidos/pages/DireccionesPage.tsx`
  - Modificado: `frontend/src/features/pedidos/components/DireccionManager.tsx`
  - Modificado: `frontend/src/features/pedidos/components/DirectionSelector.tsx`
  - Modificado: `frontend/src/features/clientes/pages/PerfilPage.tsx`
  - Modificado: `frontend/src/router.tsx`
- Sin cambios de backend: el dominio `direcciones` ya está implementado y operativo.
- Sin cambios de base de datos ni de migraciones.

## Non-Goals

- No se modifica el backend de direcciones.
- No se implementa la creación del pedido (`carrito-pedidos` / `CreateOrderButton`
  son cambios aparte); aquí solo se garantiza que el `direccionId` quede disponible.
- No se agrega creación de direcciones "inline" dentro del checkout: el flujo de alta
  redirige a `/perfil/direcciones`.
