## Why

El change `carrito-pedidos` ya referencia `direccion_id` en `CartCreateDTO` y espera resolverlo vía `uow.direcciones.get_by_id()`, pero no existe ningún modelo `DireccionEntrega`, repositorio ni endpoints para gestionarlo. Hoy `Cliente` guarda una sola `direccion: str` plana, lo que impide que un cliente tenga varias direcciones de entrega y que el checkout elija una. Esta funcionalidad es bloqueante: `carrito-pedidos` no puede archivarse hasta que las direcciones existan como feature real.

## What Changes

- Nuevo modelo de dominio `DireccionEntrega` (clase Python pura, persistencia in-memory) con campos de dirección, `cliente_id`, `es_predeterminada` y soft delete.
- Nuevo repositorio `InMemoryDireccionRepository` con CRUD por cliente y resolución de dirección predeterminada.
- `IUnitOfWork` e `InMemoryUnitOfWork` extendidos con la propiedad `direcciones`.
- Nuevo `DireccionService` con la lógica de negocio: alta, edición, baja, listado y gestión del flag predeterminada.
- Nuevos endpoints REST anidados bajo `/api/v1/clientes/me/direcciones` (CRUD + marcar predeterminada), protegidos por JWT con `require_role("client", "admin")` y propiedad enforced por `user_id`.
- Frontend: componente `DireccionSelector` (hoy stub `DirectionSelector.tsx` en `features/pedidos/`) conectado a la API real, más una UI CRUD para que el cliente gestione sus direcciones.
- El campo plano `Cliente.direccion` se conserva por compatibilidad; las direcciones de entrega del checkout pasan a vivir en `DireccionEntrega`. No es **BREAKING** para datos existentes.

## Capabilities

### New Capabilities
- `direcciones-gestion`: alta, edición, baja (soft delete) y listado de direcciones de entrega de un cliente, con regla de ownership por `user_id`.
- `direcciones-predeterminada`: lógica de dirección predeterminada — la primera dirección creada es predeterminada automáticamente y solo una puede serlo a la vez por cliente.

### Modified Capabilities
<!-- Sin cambios de requisitos sobre specs existentes. carrito-pedidos consume direcciones pero su spec no cambia. -->

## Impact

- **Backend nuevo**: `backend/modules/direcciones/` (`model.py`, `repository.py`, `service.py`, `router.py`, `schemas.py`, `exceptions.py`).
- **Backend modificado**: `backend/core/uow.py` y `backend/core/uow_inmemory.py` (propiedad `direcciones`); `backend/main.py` (registro del router).
- **Tests**: nuevos tests de servicio y endpoints en `backend/tests/modules/direcciones/`.
- **Frontend modificado**: `frontend/src/features/pedidos/components/DirectionSelector.tsx`; nuevos componentes/páginas de gestión de direcciones; cliente API nuevo.
- **Dependencia**: este change debe implementarse y archivarse ANTES de archivar `carrito-pedidos`, que consume `uow.direcciones`.
- Sin migraciones de BD ni Alembic — la persistencia es in-memory (dicts).
