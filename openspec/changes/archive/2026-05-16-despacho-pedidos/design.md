## Context

El módulo `backend/modules/pedidos/` ya crea pedidos (estado PENDIENTE) y los confirma automáticamente vía el webhook de MercadoPago implementado en `pago-gestion` (transición PENDIENTE→CONFIRMADO con decremento de stock). Existen los modelos `Pedido`, `DetallePedido`, `HistorialEstadoPedido` y el enum `EstadoPedidoEnum` con los 6 estados de la FSM.

Lo que falta es la operación manual del pedido: avanzarlo por la cadena CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO y poder cancelarlo. Hoy el router de pedidos solo expone `POST /pedidos`, `GET /pedidos` y `GET /pedidos/{id}`, todos limitados al cliente propietario.

Restricciones del entorno:
- Backend sync (sin async/await), patrón Router → Service → UoW → Repository.
- UoW in-memory (`InMemoryUnitOfWork`, `singleton_uow`). No hay Alembic ni PostgreSQL activos.
- `require_role(*roles)` en `jwt_middleware.py` actualmente devuelve **solo `user_id`**, descartando el rol. Las transiciones de la FSM dependen del rol (p. ej. EN_PREP→CANCELADO es exclusiva de ADMIN), por lo que el service necesita conocer el rol.
- `HistorialEstadoPedido` es append-only: el repositorio solo expone `create()` y `list_by_pedido()`.

## Goals / Non-Goals

**Goals:**
- Implementar la FSM manual del pedido como un mapa de transiciones validado en `PedidoService`.
- Exponer el rol del usuario autenticado al router/service sin romper los endpoints existentes.
- Restaurar stock de forma atómica al cancelar pedidos en CONFIRMADO o EN_PREPARACION.
- Listado de pedidos para gestores con filtros (estado, fecha) y paginación.
- Permitir al gestor ver el detalle de cualquier pedido y al cliente ver/seguir los suyos.
- Frontend: panel de gestión (PEDIDOS/ADMIN) y vista "Mis Pedidos" (CLIENT) con línea de tiempo.

**Non-Goals:**
- Métricas o dashboard de pedidos (cubierto en `administracion-general`).
- Notificaciones al cliente por cambio de estado (email/push) — fuera de scope.
- Edición de líneas de pedido o de la dirección una vez creado (snapshots inmutables).
- Migraciones SQL / persistencia real (el proyecto sigue con UoW in-memory).
- Reapertura de pedidos terminales.

## Decisions

### D1: FSM como mapa declarativo en el Service

Se define un diccionario de transiciones en `PedidoService` (o en `model.py`):

```python
TRANSICIONES = {
    EstadoPedidoEnum.PENDIENTE:      {EstadoPedidoEnum.CANCELADO},
    EstadoPedidoEnum.CONFIRMADO:     {EstadoPedidoEnum.EN_PREPARACION, EstadoPedidoEnum.CANCELADO},
    EstadoPedidoEnum.EN_PREPARACION: {EstadoPedidoEnum.EN_CAMINO, EstadoPedidoEnum.CANCELADO},
    EstadoPedidoEnum.EN_CAMINO:      {EstadoPedidoEnum.ENTREGADO},
    EstadoPedidoEnum.ENTREGADO:      set(),   # terminal
    EstadoPedidoEnum.CANCELADO:      set(),   # terminal
}
```

`advance_estado()` valida que `nuevo_estado in TRANSICIONES[estado_actual]`; si no, lanza `TransicionInvalida`. Esto cubre RN-FS01 (sin saltos ni retrocesos) y RN-FS06 (terminales sin salida).

**Alternativa descartada**: validar con cadenas de `if/elif` → frágil, difícil de testear y de extender.

### D2: PENDIENTE→CONFIRMADO NO se incluye en el mapa de transiciones manuales

El mapa de D1 omite deliberadamente la transición PENDIENTE→CONFIRMADO. Esa transición es exclusivamente automática (webhook MP, RN-FS02). El endpoint `PATCH /pedidos/{id}/estado` rechaza cualquier intento de pasar a CONFIRMADO con `TransicionInvalida`, garantizando que nadie la ejecute manualmente.

### D3: Autorización por transición — tabla rol→transición

Cada transición tiene roles autorizados. Se define un segundo mapa:

| Transición | Roles autorizados |
|-----------|-------------------|
| CONFIRMADO → EN_PREPARACION | PEDIDOS, ADMIN |
| EN_PREPARACION → EN_CAMINO | PEDIDOS, ADMIN |
| EN_CAMINO → ENTREGADO | PEDIDOS, ADMIN |
| PENDIENTE → CANCELADO | CLIENT (solo dueño), PEDIDOS, ADMIN |
| CONFIRMADO → CANCELADO | PEDIDOS, ADMIN |
| EN_PREPARACION → CANCELADO | ADMIN |

`advance_estado()` recibe `(pedido_id, nuevo_estado, usuario_id, rol, motivo)`. Valida primero la transición (D1), luego que `rol` esté autorizado para esa transición; si no, lanza `RolNoAutorizadoParaTransicion` (HTTP 403). Para la cancelación por CLIENT, además valida que `pedido.cliente_id == usuario_id` (RN-FS08 cubre el caso EN_PREP→CANCELADO solo ADMIN).

**Alternativa descartada**: validar el rol solo con `require_role` en el router → no permite reglas por transición (un mismo endpoint admite varias transiciones con permisos distintos).

### D4: `require_role` debe exponer el rol — devolver `CurrentUser`

Hoy `require_role(...)` devuelve `current_user.user_id` (un `int`). Para D3 el service necesita el rol. Se agrega un parámetro/variante que devuelve el objeto `CurrentUser` completo (que ya contiene `user_id`, `email`, `role`).

Para no romper los endpoints existentes que esperan un `int`, se añade una dependency nueva `require_role_user(*roles)` que retorna `CurrentUser`, y los endpoints nuevos de despacho la usan. Los endpoints viejos quedan intactos.

**Alternativa descartada**: cambiar el retorno de `require_role` a `CurrentUser` → rompería `create_order`, `list_orders`, `get_order_detail` y todos los demás módulos que dependen de `int`.

### D5: Restauración atómica de stock en cancelación

Si la transición es `* → CANCELADO` **y** el estado de origen es CONFIRMADO o EN_PREPARACION (estados en los que el stock ya fue decrementado), `advance_estado()` recorre los `DetallePedido` del pedido y por cada uno incrementa el stock del producto correspondiente, dentro de la misma operación de UoW que actualiza el estado y registra el historial. Un solo `uow.commit()` al final (RN-FS05).

Si el origen es PENDIENTE, no se restaura stock (nunca se decrementó).

El repositorio de productos expone un método `restore_stock(producto_id, cantidad)` (o `increment_stock`). Si no existe, se agrega en `backend/modules/productos/repository.py`.

### D6: Registro append-only en cada transición

Toda transición exitosa inserta un `HistorialEstadoPedido` con `estado_anterior`, `estado_nuevo`, `usuario_id` y `observacion`. La `observacion` lleva el `motivo` cuando la transición es a CANCELADO (obligatorio, RN-PE05) y un texto descriptivo en los demás casos. Se usa el `create()` existente del repositorio append-only — nunca update/delete (RN-FS07).

### D7: Motivo obligatorio al cancelar

`EstadoUpdateDTO` incluye `nuevo_estado: str` y `motivo: Optional[str]`. La validación de obligatoriedad (`motivo` requerido y no vacío cuando `nuevo_estado == "CANCELADO"`) se hace con un validator Pydantic en el schema, devolviendo HTTP 422 si falta (RN-PE05). El service también la revalida como defensa en profundidad.

### D8: Endpoint de gestión separado del listado del cliente

`GET /pedidos` (existente) sigue devolviendo solo los pedidos del cliente autenticado. Se agrega `GET /pedidos/gestion` para PEDIDOS/ADMIN que lista **todos** los pedidos con filtros opcionales `estado` y rango `fecha_desde`/`fecha_hasta`, más paginación `skip`/`limit`. El repositorio agrega `list_all_filtered(estado, fecha_desde, fecha_hasta, skip, limit)`.

`GET /pedidos/{id}` se modifica: si el rol es PEDIDOS o ADMIN, omite la validación de ownership; si es CLIENT, mantiene la validación `cliente_id == usuario_id`.

**Alternativa descartada**: un único endpoint `GET /pedidos` con comportamiento variable según rol → mezcla responsabilidades y complica el contrato de la API y los hooks del frontend.

### D9: Frontend — dos vistas, una feature

Dentro de `frontend/src/features/pedidos/` se agregan:
- `pages/GestionPedidosPage.tsx`: tabla de pedidos con filtros (estado, fecha), acceso al detalle y acciones de transición. Ruta protegida por rol PEDIDOS/ADMIN.
- `pages/MisPedidosPage.tsx`: lista de pedidos del cliente con estado actual y línea de tiempo (derivada del historial). Permite cancelar pedidos en PENDIENTE.
- Componentes compartidos: `EstadoBadge`, `EstadoTimeline`, `EstadoActions` (botones de transición según estado y rol), `PedidoFilters`.
- `pedidoClient.ts` agrega `updateEstado(id, nuevoEstado, motivo)`, `listGestion(filtros)` y `getDetalle(id)`.
- Estado servidor con TanStack Query (hooks por dominio); el cambio de estado invalida la query de listado/detalle. No se usa Zustand para esto (es estado de servidor).

## Risks / Trade-offs

- [UoW in-memory no es transaccional real] → La "atomicidad" de la restauración de stock es lógica (todo dentro de un bloque que termina en `commit()`); si una excepción ocurre a mitad, los cambios in-memory ya aplicados sobre objetos podrían no revertirse. Mitigación: validar todo (transición, rol, existencia de productos) **antes** de mutar cualquier objeto, y mutar solo al final en un bloque sin puntos de fallo.
- [Rol no presente en el token] → Si un token viejo no trae `role`, `verify_jwt_token` ya falla con 401. Sin riesgo adicional.
- [Doble cancelación concurrente restaura stock dos veces] → El mapa de transiciones lo previene: tras la primera cancelación el estado es CANCELADO (terminal), la segunda lanza `TransicionInvalida`.
- [Cliente cancela pedido ajeno] → Validación explícita `cliente_id == usuario_id` para la transición CLIENT; gestores quedan exentos por diseño (D3).
- [Filtros de fecha mal formados] → El schema/Query valida formato ISO; entrada inválida → HTTP 422.

## Migration Plan

No hay migraciones de base de datos: los modelos ya existen y el proyecto usa UoW in-memory. Pasos de despliegue:

1. Extender `jwt_middleware.py` con `require_role_user` (no rompe nada existente).
2. Agregar `restore_stock`/`increment_stock` al repositorio de productos.
3. Agregar al repositorio de pedidos `list_all_filtered`; `update_estado` ya existe.
4. Implementar `advance_estado` en `PedidoService` con los mapas FSM y rol→transición.
5. Agregar endpoints `PATCH /pedidos/{id}/estado` y `GET /pedidos/gestion`; ajustar RBAC de `GET /pedidos/{id}`.
6. Implementar vistas frontend y rutas protegidas.
7. Rollback: revertir los commits; al no haber esquema de BD nada que deshacer.

## Open Questions

- ¿La línea de tiempo del cliente muestra el `usuario_id` que hizo cada transición? → Por privacidad se mostrará solo estado + timestamp + observación, sin identidad del gestor.
- ¿Se permite a PEDIDOS cancelar desde EN_CAMINO? → No: el CLAUDE.md no lista esa transición; EN_CAMINO solo avanza a ENTREGADO. Queda fuera del mapa.
