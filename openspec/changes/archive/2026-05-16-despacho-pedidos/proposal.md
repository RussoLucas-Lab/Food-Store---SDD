## Why

Los pedidos llegan a estado CONFIRMADO tras el pago, pero no existe forma de hacerlos avanzar por su ciclo de vida operativo (preparación, envío, entrega) ni de cancelarlos. Sin esto, los roles PEDIDOS y ADMIN no pueden operar el negocio y el cliente no puede seguir el progreso de su compra. Este change implementa la gestión de despacho: la máquina de estados manual del pedido, su panel de gestión interno y la vista de seguimiento del cliente.

## What Changes

- Nuevo endpoint `PATCH /api/v1/pedidos/{id}/estado` para avanzar o cancelar el estado de un pedido, con validación de la FSM y RBAC por rol (PEDIDOS / ADMIN / CLIENT según la transición).
- Nuevo endpoint `GET /api/v1/pedidos/gestion` que lista todos los pedidos para gestores, con filtros por estado y rango de fecha y paginación.
- Reutilización de `GET /api/v1/pedidos/{id}` extendida para que gestores (PEDIDOS/ADMIN) puedan ver el detalle de cualquier pedido, no solo el propio.
- `PedidoService` incorpora `advance_estado()` con un mapa de transiciones válidas (FSM), validación de rol por transición y registro append-only en `HistorialEstadoPedido`.
- Restauración atómica de stock al cancelar un pedido en estado CONFIRMADO o EN_PREPARACION (RN-FS05).
- `require_role` / dependency de autenticación expone el rol del usuario (hoy solo expone `user_id`), necesario para distinguir las transiciones restringidas por rol.
- **Frontend**: nueva página de gestión de pedidos para PEDIDOS/ADMIN (listado con filtros, detalle, botones de transición de estado y cancelación con motivo).
- **Frontend**: nueva página "Mis Pedidos" para CLIENT (historial, estado actual y línea de tiempo del pedido), con opción de cancelar pedidos en estado PENDIENTE.

## Capabilities

### New Capabilities

- `pedido-transicion-estado`: Avance y cancelación del estado de un pedido validados contra la FSM. Define las transiciones permitidas, el rol autorizado para cada una, la obligatoriedad de motivo al cancelar, el registro append-only en el historial y la restauración atómica de stock al cancelar.
- `pedido-gestion-listado`: Listado y consulta de pedidos para los roles PEDIDOS y ADMIN, con filtros por estado y fecha, paginación y acceso al detalle de cualquier pedido.
- `pedido-despacho-frontend`: Panel de gestión de pedidos (PEDIDOS/ADMIN) y vista "Mis Pedidos" del cliente, incluyendo línea de tiempo de estados y acciones de transición.

### Modified Capabilities

<!-- No hay capabilities con specs existentes cuyo comportamiento cambie a nivel de requisito. La creación de pedido ya está cubierta por pago-gestion archivado. -->

## Impact

- **Backend**: `backend/modules/pedidos/` — `service.py` (nuevo `advance_estado` + mapa FSM + restauración de stock), `router.py` (nuevo endpoint `PATCH .../estado` y `GET .../gestion`, ajuste de RBAC en `GET .../{id}`), `schemas.py` (nuevos `EstadoUpdateDTO` y schemas de gestión), `exceptions.py` (nuevas excepciones de transición inválida y rol no autorizado).
- **Backend**: `backend/middleware/jwt_middleware.py` — `require_role` debe poder devolver el rol además del `user_id` (o un objeto `CurrentUser`), sin romper los endpoints existentes.
- **Backend**: `backend/modules/productos/` — el repositorio de productos debe exponer un método para incrementar stock (restauración al cancelar); si ya existe `decrement`, se agrega el inverso.
- **Frontend**: nueva feature/área de gestión de pedidos en `frontend/src/features/pedidos/` (páginas de gestión y de "Mis Pedidos", componentes de listado, filtros, línea de tiempo y acciones de estado), nuevos métodos en `pedidoClient.ts`, nuevas rutas en `router.tsx` protegidas por rol.
- **Sin migraciones nuevas**: los modelos `Pedido`, `DetallePedido`, `HistorialEstadoPedido` y `EstadoPedido` ya existen. El proyecto usa UoW in-memory.
- **Dependencias**: ninguna nueva.
