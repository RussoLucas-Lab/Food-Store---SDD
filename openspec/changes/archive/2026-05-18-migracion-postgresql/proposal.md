## Why

El backend actual usa almacenamiento en memoria (`singleton_uow`) — todos los datos se pierden al reiniciar el servidor. Para la entrega del TPI y para cumplir la arquitectura especificada en el CLAUDE.md (SQLModel + PostgreSQL + Alembic), es necesario migrar a una base de datos real con persistencia entre reinicios.

## What Changes

- Agregar dependencias: `sqlmodel`, `alembic`, `psycopg2-binary` a `requirements.txt`.
- Crear modelos SQLModel (tablas) para cada entidad de dominio: `Usuario`, `Categoria`, `Ingrediente`, `Producto`, `ProductoIngrediente`, `Cliente`, `DireccionEntrega`, `Pedido`, `DetallePedido`, `HistorialEstadoPedido`, `Pago`.
- Crear implementaciones PostgreSQL de cada repositorio (reemplaza las `InMemory*`).
- Crear `PostgreSQLUnitOfWork` que gestiona sesiones SQLAlchemy por request.
- **BREAKING**: Refactorizar todos los routers para usar `Depends(get_uow)` en lugar del `singleton_uow` module-level.
- Crear setup de Alembic con migración inicial que genera el schema completo.
- Actualizar `docker-compose.yml` para incluir el servicio `db` (PostgreSQL 15).
- Actualizar `backend/db/seed.py` para usar el UoW de PostgreSQL.
- Mantener `InMemoryUnitOfWork` para los tests unitarios (sin cambios en tests existentes).

## Capabilities

### New Capabilities

- `persistencia-datos`: Los datos persisten entre reinicios del servidor. El sistema usa PostgreSQL como storage principal. Las migraciones se gestionan con Alembic.

### Modified Capabilities

<!-- Los contratos de API no cambian — mismos endpoints, mismos schemas de respuesta. No hay modificaciones de specs de negocio. -->

## Impact

- **Backend** — todos los archivos `router.py` (10), nuevos `sqlmodel_model.py` (8 módulos), nuevos `postgresql_repository.py` (8 módulos), `core/uow.py`, `core/database.py`, `backend/db/seed.py`, `backend/main.py`.
- **Dependencias** — `requirements.txt`: agregar `sqlmodel>=0.0.14`, `alembic>=1.13`, `psycopg2-binary>=2.9`.
- **Infraestructura** — `docker-compose.yml`: re-habilitar servicio `db` (postgres:15). `backend/.env.example`: mantener variables `DB_*` (ya presentes).
- **Tests** — los tests unitarios existentes siguen usando `InMemoryUnitOfWork` sin cambios. Los tests de integración se adaptan para usar la BD real vía fixture.
- **Datos** — los datos en memoria se pierden al migrar (solo afecta al entorno de desarrollo; el seed recarga los datos iniciales).
