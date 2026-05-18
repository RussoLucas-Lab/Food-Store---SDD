# Design — direcciones-cliente

## Context

El backend de direcciones de entrega está completo en `backend/modules/direcciones/`
y expone 5 endpoints REST bajo `/api/v1/clientes/me/direcciones`:

| Método | Ruta | Acción |
|--------|------|--------|
| POST   | `/clientes/me/direcciones` | crear dirección |
| GET    | `/clientes/me/direcciones` | listar direcciones activas |
| PUT    | `/clientes/me/direcciones/{id}` | actualizar dirección |
| DELETE | `/clientes/me/direcciones/{id}` | baja lógica (soft-delete) |
| PUT    | `/clientes/me/direcciones/{id}/predeterminada` | marcar predeterminada |

Reglas de negocio ya garantizadas por el service backend:
- **RN-DI01**: la primera dirección de un cliente queda automáticamente como predeterminada.
- **RN-DI02**: marcar una dirección como predeterminada desmarca al resto.
- **Soft-delete**: `DELETE` setea `deleted_at`; las direcciones eliminadas no aparecen en `GET`.

En el frontend ya existen `direccionClient.ts`, `DireccionManager.tsx`,
`DirectionSelector.tsx` y la integración en `CheckoutPage.tsx`. Lo que falta es
estandarizar la capa de datos según la convención FSD del proyecto y hacer la
funcionalidad alcanzable desde la navegación.

Estado actual relevante:
- `DireccionManager` y `DirectionSelector` llaman directamente a `direccionClient` y
  declaran sus propias `useQuery`/`useMutation` inline. Esto duplica la `queryKey` y la
  política de invalidación, contradiciendo la convención `features/<dominio>/hooks/`
  (ver `usePedidos.ts` como referencia).
- `PerfilPage` no monta `DireccionManager`, por lo que no hay forma de gestionar
  direcciones desde la UI.
- `DirectionSelector` enlaza a `/perfil` (que no contiene gestión de direcciones).

## Goals / Non-Goals

**Goals:**
- Centralizar el estado de servidor de direcciones en hooks TanStack Query
  reutilizables, alineados con la convención del proyecto.
- Hacer la gestión CRUD de direcciones alcanzable desde el perfil y desde una ruta
  dedicada.
- Garantizar que el checkout pueda seleccionar una dirección y obtener su `id`.
- No alterar el comportamiento visible de los componentes existentes (refactor
  conservador).

**Non-Goals:**
- Modificar el backend de direcciones.
- Implementar la creación del pedido (`CreateOrderButton` pertenece a `carrito-pedidos`).
- Alta de dirección "inline" dentro del checkout (se redirige a la página dedicada).
- Validación geográfica / autocompletado de direcciones.

## Decisions

### D1 — Hooks centralizados en `features/pedidos/hooks/useDirecciones.ts`

Se crea un módulo de hooks que encapsula TanStack Query, espejando el patrón de
`usePedidos.ts`:

- `useDirecciones()` → `useQuery({ queryKey: ['direcciones'], queryFn: getDirecciones })`.
- `useCreateDireccion()` → `useMutation`, `onSuccess` invalida `['direcciones']`.
- `useUpdateDireccion()` → `useMutation` con `{ id, dto }`, invalida `['direcciones']`.
- `useDeleteDireccion()` → `useMutation`, invalida `['direcciones']`.
- `useSetDireccionPredeterminada()` → `useMutation`, invalida `['direcciones']`.

Se exporta una constante `DIRECCIONES_QUERY_KEY = ['direcciones']` como fuente única.

**Por qué**: la lógica de servidor inline en componentes viola la separación FSD
(Pages → Features → Hooks → API → Types) y duplica la `queryKey`. Centralizar evita
desincronización de caché y facilita el testeo.
**Alternativa descartada**: dejar la lógica inline — rechazado por inconsistencia con
`usePedidos.ts` y riesgo de `queryKey` divergentes.

### D2 — Pertenencia del dominio: `features/pedidos`

Los hooks, componentes y la página de direcciones viven bajo `features/pedidos/`,
donde ya residen `direccionClient.ts`, `DireccionManager.tsx` y `DirectionSelector.tsx`.

**Por qué**: las direcciones de entrega son un insumo del pedido y los archivos ya
están allí; moverlos a un feature nuevo `direcciones/` rompería imports y no aporta
valor en el alcance académico.
**Alternativa descartada**: crear `features/direcciones/` — más correcto en abstracto,
pero implicaría mover y reescribir imports de código que ya funciona.

### D3 — Refactor conservador de componentes existentes

`DireccionManager` y `DirectionSelector` se reescriben para consumir los hooks de D1,
sin cambiar markup, `data-testid`, props ni comportamiento. La pre-selección de la
predeterminada en `DirectionSelector` se mantiene idéntica.

**Por qué**: minimiza el riesgo de regresión visual; el cambio es puramente de la
capa de datos.

### D4 — Página dedicada `/perfil/direcciones` + sección en el perfil

- Nueva página `DireccionesPage.tsx` que renderiza `<DireccionManager />` dentro del
  `Layout` ya aplicado por `LayoutRoute`.
- Nueva ruta protegida `/perfil/direcciones` dentro del bloque `ProtectedRoute` que ya
  cubre `/perfil`.
- `PerfilPage` monta además `<DireccionManager />` como sección "Mis Direcciones",
  para que la gestión esté visible directamente desde el perfil.

**Por qué**: el brief pide tanto una ruta dedicada como acceso desde el perfil;
ambos comparten el mismo componente, sin duplicar lógica.
**Alternativa descartada**: solo la sección en el perfil — se descarta porque
`DirectionSelector` necesita un destino de enlace estable (`/perfil/direcciones`).

### D5 — Selección de dirección en checkout

`CheckoutPage` ya mantiene `selectedDirectionId` en estado local y lo pasa a
`CreateOrderButton`. Se mantiene ese contrato. `DirectionSelector` actualiza sus
enlaces "Agregar Nueva Dirección" para apuntar a `/perfil/direcciones`. Si el cliente
no tiene direcciones, `DirectionSelector` ya muestra el prompt para crear una.

**Por qué**: el estado de selección es estado de UI efímero del checkout; no necesita
persistirse en `cartStore`. Mantenerlo local respeta la separación Zustand (cliente)
vs estado efímero de página.
**Alternativa descartada**: guardar `direccionId` en `cartStore` — innecesario, el id
solo se usa en el momento de crear el pedido y no debe sobrevivir a recargas.

## Risks / Trade-offs

- **Regresión visual en el refactor de componentes** → mitigación: refactor que toca
  solo la capa de datos; se conservan markup y `data-testid`; verificación manual del
  flujo perfil → direcciones → checkout.
- **`queryKey` divergente si quedan llamadas inline** → mitigación: D1 exporta la
  constante `DIRECCIONES_QUERY_KEY` y se elimina toda `useQuery`/`useMutation` inline
  de direcciones.
- **`PerfilPage` usa CSS propio (`PerfilPage.css`) mientras `DireccionManager` usa
  Tailwind** → mitigación: montar `DireccionManager` en un contenedor neutro; la
  inconsistencia estética es aceptable en el alcance del TPI.
- **Doble punto de entrada (sección en perfil + página dedicada)** → trade-off
  aceptado: ambos reutilizan el mismo componente, sin duplicar lógica.

## Migration Plan

No hay migración de datos ni de backend. Despliegue puramente de frontend:
1. Agregar `useDirecciones.ts`.
2. Refactorizar `DireccionManager` y `DirectionSelector` para usar los hooks.
3. Agregar `DireccionesPage` y la ruta.
4. Integrar la sección en `PerfilPage`.

Rollback: revertir el commit de frontend; el backend no se ve afectado.

## Open Questions

- ¿La ruta canónica debe ser `/perfil/direcciones` o `/mi-cuenta/direcciones`?
  Se adopta `/perfil/direcciones` por consistencia con la ruta `/perfil` existente.
- ¿`PerfilPage` debería migrar a Tailwind para uniformidad? Fuera de alcance de este
  cambio.
