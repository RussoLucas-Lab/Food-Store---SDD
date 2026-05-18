## 1. Backend — autenticación con rol

- [x] 1.1 Agregar `require_role_user(*roles)` en `backend/middleware/jwt_middleware.py` que devuelve el objeto `CurrentUser` completo (user_id + email + role), sin modificar `require_role` existente
- [x] 1.2 Verificar que los endpoints existentes que usan `require_role` siguen recibiendo un `int` (sin regresiones)

## 2. Backend — repositorios

- [x] 2.1 Agregar `restore_stock(producto_id, cantidad)` (o `increment_stock`) al repositorio de productos en `backend/modules/productos/repository.py`
- [x] 2.2 Agregar `list_all_filtered(estado, fecha_desde, fecha_hasta, skip, limit)` a `InMemoryPedidoRepository` en `backend/modules/pedidos/repository.py`

## 3. Backend — FSM y excepciones

- [x] 3.1 Definir el mapa `TRANSICIONES` (estado → estados destino válidos) en `backend/modules/pedidos/model.py` o `service.py`, omitiendo deliberadamente PENDIENTE→CONFIRMADO
- [x] 3.2 Definir el mapa de autorización rol→transición según la tabla del design (D3)
- [x] 3.3 Agregar excepciones `TransicionInvalida` y `RolNoAutorizadoParaTransicion` en `backend/modules/pedidos/exceptions.py`

## 4. Backend — schemas

- [x] 4.1 Crear `EstadoUpdateDTO` en `backend/modules/pedidos/schemas.py` con `nuevo_estado: str` y `motivo: Optional[str]`, y validator que exige `motivo` no vacío cuando `nuevo_estado == "CANCELADO"`
- [x] 4.2 Crear schema de respuesta para el listado de gestión (resumen de pedido con cliente, estado, total, fecha)

## 5. Backend — service

- [x] 5.1 Implementar `PedidoService.advance_estado(pedido_id, nuevo_estado, usuario_id, rol, motivo)`: valida existencia del pedido, valida transición contra `TRANSICIONES`, valida rol contra el mapa de autorización, valida ownership cuando el rol es CLIENT
- [x] 5.2 En `advance_estado`, restaurar stock atómicamente cuando se cancela un pedido cuyo estado de origen es CONFIRMADO o EN_PREPARACION; no restaurar si el origen es PENDIENTE
- [x] 5.3 En `advance_estado`, registrar la transición en `HistorialEstadoPedido` (append-only) con estado anterior, nuevo, usuario y observación/motivo, y hacer un único `uow.commit()`
- [x] 5.4 Implementar `PedidoService.list_gestion(estado, fecha_desde, fecha_hasta, skip, limit)` que devuelve todos los pedidos filtrados
- [x] 5.5 Modificar `get_order_detail` para que acepte el rol: omitir validación de ownership cuando el rol es PEDIDOS o ADMIN

## 6. Backend — router

- [x] 6.1 Agregar endpoint `PATCH /api/v1/pedidos/{id}/estado` usando `require_role_user`, mapeando excepciones a HTTP (404 not found, 409 transición inválida, 403 rol no autorizado, 422 motivo faltante)
- [x] 6.2 Agregar endpoint `GET /api/v1/pedidos/gestion` restringido a roles PEDIDOS y ADMIN, con query params `estado`, `fecha_desde`, `fecha_hasta`, `skip`, `limit`
- [x] 6.3 Ajustar `GET /api/v1/pedidos/{id}` para usar el rol: gestores ven cualquier pedido, CLIENT solo el propio

## 7. Frontend — cliente de API y hooks

- [x] 7.1 Agregar a `frontend/src/features/pedidos/services/pedidoClient.ts` los métodos `updateEstado(id, nuevoEstado, motivo)`, `listGestion(filtros)` y `getDetalle(id)`
- [x] 7.2 Crear hooks de TanStack Query para el listado de gestión, el detalle de pedido y la mutación de cambio de estado (invalida listado y detalle al éxito)

## 8. Frontend — componentes compartidos

- [x] 8.1 Crear `EstadoBadge` que muestra el estado del pedido con estilo según el estado
- [x] 8.2 Crear `EstadoTimeline` que renderiza la línea de tiempo de estados a partir del historial
- [x] 8.3 Crear `EstadoActions` que muestra solo los botones de transición válidos según estado y rol, con diálogo de motivo obligatorio para cancelar
- [x] 8.4 Crear `PedidoFilters` con selector de estado y rango de fechas

## 9. Frontend — páginas y rutas

- [x] 9.1 Crear `GestionPedidosPage.tsx` en `frontend/src/features/pedidos/pages/` con tabla de pedidos, filtros, detalle y acciones de transición
- [x] 9.2 Crear `MisPedidosPage.tsx` en `frontend/src/features/pedidos/pages/` con lista de pedidos del cliente, detalle, línea de tiempo y cancelación de pedidos en PENDIENTE
- [x] 9.3 Agregar las rutas en `frontend/src/router.tsx`: gestión protegida por rol PEDIDOS/ADMIN, "Mis Pedidos" protegida por rol CLIENT

## 10. Tests

- [x] 10.1 Tests de `advance_estado`: transiciones válidas, salto/retroceso rechazado, estados terminales, PENDIENTE→CONFIRMADO rechazada
- [x] 10.2 Tests de autorización: cliente no avanza, PEDIDOS no cancela desde EN_PREPARACION, ADMIN sí, cliente no cancela pedido ajeno
- [x] 10.3 Tests de restauración de stock: cancelar CONFIRMADO restaura stock, cancelar PENDIENTE no lo altera
- [x] 10.4 Tests de motivo obligatorio al cancelar y de registro append-only en el historial
- [x] 10.5 Tests del endpoint `GET /pedidos/gestion`: acceso por rol, filtros por estado y fecha, paginación
- [x] 10.6 Tests de `get_order_detail`: gestor accede a pedido ajeno, cliente bloqueado en pedido ajeno
