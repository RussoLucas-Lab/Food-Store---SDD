## Why

El backend está organizado por tipo técnico (`models/`, `repositories/`, `uow/`, `backend/services/`, `backend/routers/`, `backend/schemas/`) en lugar de por feature, lo que contradice la arquitectura definida en CLAUDE.md y dificulta escalar los changes restantes (carrito-pedidos, pago-gestion, despacho-pedidos). Hacer el refactor ahora, antes de implementar carrito-pedidos, evita que el desfase arquitectónico se acumule.

## What Changes

- **BREAKING (interno)**: Se eliminarán los directorios raíz `models/`, `repositories/`, `uow/`, `config/` y las carpetas `backend/services/`, `backend/routers/`, `backend/schemas/`.
- Se crea `backend/modules/` con un subdirectorio por feature: `auth`, `categorias`, `ingredientes`, `productos`, `clientes`, `pedidos`.
- Cada módulo contiene: `model.py`, `repository.py`, `service.py`, `schemas.py`, `router.py` (y `exceptions.py` donde aplica).
- Se crea `backend/core/` con los componentes transversales: `uow.py`, `uow_inmemory.py`, `security.py`, `config.py`.
- Se actualizan todos los imports en código y tests para reflejar las nuevas rutas.
- No hay cambios de lógica de negocio, APIs ni comportamiento externo — es un refactor puramente organizacional.

## Capabilities

### New Capabilities

- Ninguna. Este change no introduce nuevas funcionalidades.

### Modified Capabilities

- Ninguna. Las APIs expuestas y las reglas de negocio no cambian — solo la organización interna del código.

## Impact

- **Código afectado**: ~75–80 archivos (modelos, repositorios, servicios, routers, schemas, UoW, config, tests).
- **APIs**: Sin cambios. Los endpoints `/api/v1/*` responden igual.
- **Tests**: Todos los tests existentes deben pasar tras actualizar sus imports. No se elimina ni modifica lógica testeada.
- **Dependencias**: Sin cambios en `requirements.txt`.
- **Changes futuros**: `carrito-pedidos` y todos los siguientes nacen directamente en la nueva estructura.
