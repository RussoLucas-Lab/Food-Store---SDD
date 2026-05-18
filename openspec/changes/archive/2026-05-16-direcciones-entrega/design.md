## Context

El change `carrito-pedidos` está al 92% (60/65 tareas) y su `CartCreateDTO` ya incluye `direccion_id`; el `PedidoService` espera resolverlo con `uow.direcciones.get_by_id()` y lanza `DireccionNotFound` si no existe. Sin embargo no hay modelo `DireccionEntrega`, ni repositorio, ni propiedad `direcciones` en el UoW. Hoy `Cliente` solo tiene un campo plano `direccion: str`, insuficiente para un cliente con varias direcciones.

Restricciones del proyecto (TPI académico):
- Persistencia **in-memory** con dicts Python. Sin SQLModel, sin Alembic, sin BD.
- Arquitectura feature-first y capas estrictamente unidireccionales: Router → Service → UoW → Repository → Model.
- Repositorios con prefijo `InMemory` e interfaz `ABC` (`I<Nombre>Repository`).
- Auth por JWT con `require_role()`; el `user_id` se obtiene del token.
- Schemas Pydantic v2 separados Create / Update / Read.
- El Service nunca llama `commit()` directo — lo hace el UoW.

Este change es **bloqueante**: `carrito-pedidos` no puede archivarse hasta que las direcciones existan como feature real.

## Goals / Non-Goals

**Goals:**

- Modelo `DireccionEntrega` puro en Python, in-memory, con `cliente_id`, campos de dirección, `es_predeterminada` y soft delete (`activo`).
- Repositorio `InMemoryDireccionRepository` con CRUD por cliente, filtrado por propietario y `get_by_id` consumible por `carrito-pedidos`.
- Extender `IUnitOfWork` e `InMemoryUnitOfWork` con la propiedad `direcciones`.
- `DireccionService` que centralice ownership (RN-DI03), regla de primera predeterminada (RN-DI01), unicidad de predeterminada (RN-DI02) y reasignación al eliminar.
- Endpoints REST anidados bajo `/api/v1/clientes/me/direcciones`.
- Frontend: conectar `DirectionSelector` a la API real y agregar UI CRUD de direcciones.

**Non-Goals:**

- No se migra ni elimina el campo `Cliente.direccion`; se conserva por compatibilidad.
- No se persiste en BD ni se introduce Alembic.
- No se valida formato geográfico real (código postal/provincia contra catálogo).
- No se modifica el spec de `carrito-pedidos`; solo se le provee la dependencia que ya consume.
- No se gestionan direcciones para roles ADMIN/STOCK/PEDIDOS más allá del acceso `client+admin` ya usado en pedidos.

## Decisions

### D1 — Módulo nuevo `backend/modules/direcciones/`

Se crea un módulo dedicado en lugar de incrustar las direcciones dentro de `clientes/`. Cada feature es autocontenida y `carrito-pedidos` resuelve `uow.direcciones`, lo que se mapea naturalmente a un repositorio propio. El módulo contiene `model.py`, `repository.py`, `service.py`, `router.py`, `schemas.py`, `exceptions.py`, espejando la estructura de `pedidos/`.

*Alternativa considerada*: ubicar todo en `clientes/`. Descartada porque mezclaría dos agregados y complicaría el wiring del UoW (`uow.direcciones` quedaría implícito).

### D2 — Modelo `DireccionEntrega`

Clase Python pura siguiendo el patrón de `Cliente` (`__init__`, `__repr__`, `to_dict`). Campos:

- `id: int` — PK autoincremental gestionada por el repositorio.
- `cliente_id: int` — propietario; coincide con el `user_id` del JWT.
- `calle: str`, `numero: str`, `ciudad: str`, `provincia: str`, `codigo_postal: str` — obligatorios.
- `piso: Optional[str]`, `departamento: Optional[str]`, `referencia: Optional[str]` — opcionales.
- `es_predeterminada: bool` — default `False`, el servicio aplica RN-DI01.
- `activo: bool` — soft delete, default `True`.
- `created_at`, `updated_at: datetime`.

`numero` se modela como `str` para admitir valores tipo "S/N" o "1234 bis".

### D3 — `InMemoryDireccionRepository`

Interfaz `IDireccionRepository` (ABC) + implementación in-memory con `dict[int, DireccionEntrega]` y `_next_id`. Métodos:

- `create(cliente_id, **campos) -> DireccionEntrega`
- `get_by_id(direccion_id) -> Optional[DireccionEntrega]` — usado por `carrito-pedidos`; devuelve solo direcciones activas.
- `list_by_cliente(cliente_id) -> List[DireccionEntrega]` — solo activas.
- `update(direccion_id, **campos) -> Optional[DireccionEntrega]`
- `soft_delete(direccion_id) -> bool`
- `set_predeterminada(direccion_id) -> Optional[DireccionEntrega]` — marca una; el servicio coordina el desmarcado.
- `count_by_cliente(cliente_id) -> int` — para RN-DI01.

El repositorio **no** valida ownership ni reglas de negocio; eso vive en el servicio. El repositorio mantiene la invariante de unicidad de predeterminada (al setear una, desmarca el resto del mismo cliente) para que el dato nunca quede inconsistente aunque se llame directo.

### D4 — `DireccionService` concentra las reglas de negocio

- **RN-DI03 (ownership)**: cada operación que recibe un `direccion_id` verifica que `direccion.cliente_id == user_id`; si no, lanza `UnauthorizedDireccionAccess` (→ HTTP 403). Si la dirección no existe, lanza `DireccionNotFound` (→ HTTP 404).
- **RN-DI01 (primera predeterminada)**: en `create`, si `count_by_cliente(user_id) == 0`, fuerza `es_predeterminada = True` aunque el cliente no lo pida.
- **RN-DI02 (única predeterminada)**: al crear con `es_predeterminada=True` o al llamar `set_predeterminada`, el servicio garantiza que las demás direcciones del cliente queden en `False`.
- **Reasignación al borrar**: si se elimina la dirección predeterminada y quedan otras activas, el servicio promueve la más antigua (menor `id`) a predeterminada.

El servicio nunca hace `commit()` directo: lo realiza el UoW (patrón del proyecto).

### D5 — Endpoints REST anidados bajo cliente autenticado

Router con prefijo `/clientes/me/direcciones` (el `/api/v1` lo agrega `main.py`). Se usa `me` en lugar de `{cliente_id}` para reforzar que el cliente solo opera sobre lo suyo; el `cliente_id` proviene del JWT.

| Método | Ruta | Acción |
|--------|------|--------|
| `POST` | `/clientes/me/direcciones` | Crear dirección |
| `GET` | `/clientes/me/direcciones` | Listar direcciones propias |
| `PUT` | `/clientes/me/direcciones/{id}` | Editar dirección propia |
| `DELETE` | `/clientes/me/direcciones/{id}` | Eliminar (soft delete) |
| `PUT` | `/clientes/me/direcciones/{id}/predeterminada` | Marcar como predeterminada |

Todos protegidos con `Depends(require_role("client", "admin"))`, igual que el router de `pedidos`. El router instancia UoW y Service a nivel de módulo, siguiendo el patrón existente.

*Alternativa considerada*: `/direcciones` plano. Descartada: el prefijo `me` deja la propiedad explícita en la URL y es coherente con un panel de cliente.

### D6 — Schemas Pydantic v2 separados

- `DireccionCreate`: campos obligatorios + opcionales + `es_predeterminada: bool = False`. Sin `cliente_id` (se toma del JWT).
- `DireccionUpdate`: todos los campos opcionales para edición parcial.
- `DireccionResponse`: incluye `id`, `cliente_id`, `es_predeterminada`, `activo`, timestamps.

### D7 — Frontend: `DirectionSelector` real + UI CRUD

`frontend/src/features/pedidos/components/DirectionSelector.tsx` (hoy stub) se conecta a un nuevo `direccionClient.ts` que llama a `/api/v1/clientes/me/direcciones`. Se carga el listado vía TanStack Query y el componente expone la dirección seleccionada para el `CartCreateDTO`. La UI de gestión (alta/edición/baja) se ubica en `features/pedidos/` por proximidad al checkout, dentro de un componente `DireccionManager` reutilizable; así el checkout puede gestionar direcciones sin salir del flujo. Estado de servidor en TanStack Query, no en Zustand.

### D8 — Wiring en UoW y `main.py`

Se agrega la propiedad abstracta `direcciones` en `IUnitOfWork` y su implementación en `InMemoryUnitOfWork` (`self._direcciones = InMemoryDireccionRepository()`). El router se registra en `backend/main.py` junto al resto. `carrito-pedidos` pasa a tener su dependencia `uow.direcciones` satisfecha sin cambios en su código.

## Risks / Trade-offs

- **UoW separado por router** → el módulo `pedidos` y el módulo `direcciones` instancian cada uno su propio `InMemoryUnitOfWork`, por lo que una dirección creada vía la API de direcciones NO es visible para la UoW de pedidos (almacenamiento en memoria distinto). → *Mitigación*: documentar la limitación y, en `carrito-pedidos`/integración, considerar un UoW compartido (singleton) o una capa de seed común para tests. Para el alcance académico in-memory se acepta; se deja anotado en Open Questions.
- **`Cliente.direccion` plano conservado** → coexisten dos fuentes de dirección. → *Mitigación*: el checkout usa exclusivamente `DireccionEntrega`; `Cliente.direccion` queda como dato legado de perfil y no se usa para pedidos.
- **Persistencia in-memory** → los datos se pierden al reiniciar el backend. → *Mitigación*: es una restricción aceptada del TPI; los tests siembran datos explícitamente.
- **Reasignación de predeterminada por "menor id"** → la nueva predeterminada tras un borrado es la más antigua, no necesariamente la preferida por el cliente. → *Mitigación*: comportamiento determinista y documentado; el cliente puede re-marcar cuál quiere.

## Migration Plan

1. Crear el módulo `backend/modules/direcciones/` completo (model, repository, schemas, exceptions, service, router).
2. Extender `IUnitOfWork` e `InMemoryUnitOfWork` con `direcciones`.
3. Registrar el router en `backend/main.py`.
4. Agregar tests de servicio y endpoints en `backend/tests/modules/direcciones/`.
5. Implementar `direccionClient.ts` y conectar `DirectionSelector`; agregar la UI CRUD.
6. Verificar que `carrito-pedidos` resuelve `uow.direcciones.get_by_id()` sin errores.
7. Archivar `direcciones-entrega` ANTES de archivar `carrito-pedidos`.

Rollback: al ser un módulo aislado, revertir consiste en quitar el módulo, la propiedad `direcciones` del UoW y el registro del router; `carrito-pedidos` vuelve a tener su dependencia sin satisfacer.

## Open Questions

- ¿Debe `carrito-pedidos` y `direcciones` compartir una única instancia de `InMemoryUnitOfWork` (singleton) para que las direcciones creadas sean visibles al crear pedidos? Recomendado resolver durante `carrito-pedidos` o en el change de integración.
- ¿Se expone un endpoint admin para listar direcciones de cualquier cliente? Fuera de alcance de este change; se evalúa en `administracion-general`.
