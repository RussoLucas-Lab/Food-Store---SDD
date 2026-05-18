## Context

El backend tiene 8 módulos de dominio con modelos Python puros y repositorios `InMemory*`. Todos los routers importan un `singleton_uow` a nivel de módulo. La capa de acceso a datos necesita reemplazarse por SQLModel + PostgreSQL, manteniendo intactos los contratos de API (schemas Pydantic, endpoints, lógica de negocio en services).

## Goals / Non-Goals

**Goals:**
- Los datos persisten entre reinicios del servidor.
- `alembic upgrade head` en BD limpia crea el schema completo sin errores.
- El seed carga datos iniciales via PostgreSQL al arrancar.
- Los tests unitarios existentes siguen pasando sin cambios (usan `InMemoryUoW`).
- Los contratos de API (endpoints, schemas de respuesta) no cambian.

**Non-Goals:**
- Migración de datos existentes (no hay datos en prod, solo en memoria).
- Cambiar la lógica de negocio en los services.
- Cambiar los schemas Pydantic de request/response.
- Agregar async I/O (se usa SQLAlchemy síncrono para simplificar).

## Decisions

### D-01: SQLModel como ORM

**Decisión**: Usar `sqlmodel` (SQLModel) que combina SQLAlchemy + Pydantic v2 en una sola clase.

**Alternativas**: SQLAlchemy ORM puro (más verbose, requiere definir modelos dos veces: ORM + Pydantic). Tortoise ORM (async, pero introduce complejidad innecesaria).

**Razón**: El CLAUDE.md especifica SQLModel. Es la elección más natural con FastAPI. Reduce duplicación entre modelos de BD y schemas de validación.

### D-02: SQLAlchemy síncrono (no async)

**Decisión**: Usar el engine síncrono de SQLAlchemy con `Session`, no `AsyncSession`.

**Razón**: Todos los routers y services existentes son síncronos. Migrar a async requeriría refactorizar todos los endpoints. El rendimiento síncrono es suficiente para el TPI.

### D-03: Dependency injection por request con `Depends(get_db)`

**Decisión**: Reemplazar el `singleton_uow` module-level por una sesión por request inyectada via `Depends`.

```python
# core/database.py
def get_db():
    with Session(engine) as session:
        yield session

# router.py
def get_uow(session: Session = Depends(get_db)) -> PostgreSQLUnitOfWork:
    return PostgreSQLUnitOfWork(session)
```

**Razón**: El singleton compartido es un antipatrón para BD real — múltiples requests simultáneos compartirían la misma sesión/transacción. Cada request necesita su propia sesión para aislamiento transaccional correcto.

### D-04: Mantener interfaces de repositorio existentes

**Decisión**: Las implementaciones `PostgreSQL*Repository` implementan las mismas interfaces abstractas (`IUsuarioRepository`, `ICategoriaRepository`, etc.) que los `InMemory*`. Los services no cambian.

**Razón**: Bajo acoplamiento. Los services solo conocen la interfaz, no la implementación concreta. Los tests siguen usando `InMemory*` sin modificaciones.

### D-05: Un modelo SQLModel por entidad, en `sqlmodel_model.py`

**Decisión**: Crear `backend/modules/<modulo>/sqlmodel_model.py` con las tablas SQLModel. Los `model.py` existentes (modelos de dominio puros) se mantienen para retro-compatibilidad con tests.

**Razón**: Evita romper los tests unitarios que instancian los modelos de dominio directamente. La coexistencia es temporal — en un refactor futuro se unificarían.

### D-06: Alembic con autogenerate

**Decisión**: Configurar Alembic para importar todos los modelos SQLModel y usar `--autogenerate` para la migración inicial.

**Razón**: Evita escribir SQL a mano. El autogenerate de Alembic es confiable con SQLModel/SQLAlchemy.

## Risks / Trade-offs

- **[Riesgo] Coexistencia de `model.py` y `sqlmodel_model.py`**: Duplicación temporal de definiciones de entidad. → Mitigación: documentar que `sqlmodel_model.py` es la fuente de verdad para BD; `model.py` es legacy para tests.
- **[Riesgo] Conversión entre modelos SQLModel y modelos de dominio**: Los services reciben objetos `model.py` pero los repos PostgreSQL trabajan con `sqlmodel_model.py`. → Mitigación: los repos devuelven objetos de dominio (conversión interna en cada repo).
- **[Riesgo] Tests de integración**: Los tests de integración actuales usan `InMemoryUoW`. Con BD real necesitan fixture de BD. → Mitigación: agregar fixture de sesión PostgreSQL solo para tests de integración; los unitarios no cambian.

## Migration Plan

1. Agregar dependencias a `requirements.txt`.
2. Crear `backend/core/database.py` (engine, `get_db`).
3. Crear modelos SQLModel para cada módulo (`sqlmodel_model.py`).
4. Inicializar Alembic y generar migración inicial con `--autogenerate`.
5. Crear `PostgreSQLUnitOfWork` en `backend/core/uow_postgresql.py`.
6. Implementar `PostgreSQL*Repository` para cada módulo.
7. Refactorizar routers: reemplazar `uow = singleton_uow` por `Depends(get_uow)`.
8. Actualizar `backend/db/seed.py` para usar la BD real.
9. Actualizar `docker-compose.yml` para incluir servicio `db`.
10. Verificar: `docker compose up` → `alembic upgrade head` → `make seed` → login admin.

**Rollback**: si algo falla, revertir el commit y el `singleton_uow` vuelve a funcionar.
