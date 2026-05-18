## 1. Dependencias y configuración base

- [x] 1.1 Agregar a `requirements.txt`: `sqlmodel>=0.0.14`, `alembic>=1.13`, `psycopg2-binary>=2.9`
- [x] 1.2 Crear `backend/core/database.py` con engine SQLAlchemy, `get_db()` (session por request) y `create_all_tables()`
- [x] 1.3 Crear `backend/core/uow_postgresql.py` con `PostgreSQLUnitOfWork` que recibe una `Session` y expone todos los repos PG
- [x] 1.4 Crear `backend/core/deps.py` con `get_uow(session = Depends(get_db)) -> PostgreSQLUnitOfWork`

## 2. Modelos SQLModel (tablas)

- [x] 2.1 Crear `backend/modules/auth/sqlmodel_model.py` — tabla `usuarios` (id, email, password_hash, role, is_active, created_at, updated_at)
- [x] 2.2 Crear `backend/modules/categorias/sqlmodel_model.py` — tabla `categorias` (id, nombre, descripcion, is_active, deleted_at)
- [x] 2.3 Crear `backend/modules/ingredientes/sqlmodel_model.py` — tabla `ingredientes` (id, nombre, es_alergeno, deleted_at)
- [x] 2.4 Crear `backend/modules/productos/sqlmodel_model.py` — tablas `productos` y `producto_categoria` M2M
- [x] 2.5 Crear `backend/modules/clientes/sqlmodel_model.py` — tabla `clientes` (id, nombre, email, telefono, direccion, activo, user_id FK, timestamps)
- [x] 2.6 Crear `backend/modules/direcciones/sqlmodel_model.py` — tabla `direcciones_entrega` (id, cliente_id FK, calle, ciudad, es_predeterminada, deleted_at)
- [x] 2.7 Crear `backend/modules/pedidos/sqlmodel_model.py` — tablas `pedidos`, `detalle_pedido`, `historial_estado_pedido`
- [x] 2.8 Crear `backend/modules/pagos/sqlmodel_model.py` — tabla `pagos` (id, pedido_id FK, mp_payment_id, mp_status, external_reference UQ, idempotency_key UQ, timestamps)

## 3. Setup de Alembic

- [x] 3.1 Inicializar Alembic en raíz: `alembic init alembic` (desde directorio del proyecto)
- [x] 3.2 Configurar `alembic/env.py` para importar todos los modelos SQLModel y usar `DATABASE_URL` del entorno
- [x] 3.3 Generar migración inicial: `alembic revision --autogenerate -m "initial_schema"`
- [x] 3.4 Verificar el archivo de migración generado — revisar que incluya todas las tablas esperadas

## 4. Repositorios PostgreSQL

- [x] 4.1 Crear `backend/modules/auth/postgresql_repository.py` completo — implementa `IUsuarioRepository` con `Session` SQLModel
- [x] 4.2 Crear `backend/modules/categorias/postgresql_repository.py` — implementa `ICategoriaRepository`
- [x] 4.3 Crear `backend/modules/ingredientes/postgresql_repository.py` — implementa `IIngredienteRepository`
- [x] 4.4 Crear `backend/modules/productos/postgresql_repository.py` — implementa `IProductRepository` e `IProductIngredientRepository`
- [x] 4.5 Crear `backend/modules/clientes/postgresql_repository.py` — implementa `IClienteRepository`
- [x] 4.6 Crear `backend/modules/direcciones/postgresql_repository.py` — implementa `IDireccionRepository`
- [x] 4.7 Crear `backend/modules/pedidos/postgresql_repository.py` — implementa `IPedidoRepository`, `IDetallePedidoRepository`, `IHistorialEstadoPedidoRepository`
- [x] 4.8 Crear `backend/modules/pagos/postgresql_repository.py` — implementa `IPagoRepository`
- [x] 4.9 Crear `backend/modules/admin/postgresql_repository.py` — implementa `IAdminRepository` con queries de métricas via SQL

## 5. Refactor de routers (inyección de dependencias)

- [x] 5.1 Refactorizar `backend/modules/auth/router.py` — reemplazar `uow = singleton_uow` por `uow: PostgreSQLUnitOfWork = Depends(get_uow)`
- [x] 5.2 Refactorizar `backend/modules/categorias/router.py`
- [x] 5.3 Refactorizar `backend/modules/ingredientes/router.py`
- [x] 5.4 Refactorizar `backend/modules/productos/router.py`
- [x] 5.5 Refactorizar `backend/modules/clientes/router.py`
- [x] 5.6 Refactorizar `backend/modules/direcciones/router.py`
- [x] 5.7 Refactorizar `backend/modules/pedidos/router.py`
- [x] 5.8 Refactorizar `backend/modules/pagos/router.py`
- [x] 5.9 Refactorizar `backend/modules/admin/router.py`

## 6. Seed y arranque

- [x] 6.1 Refactorizar `backend/db/seed.py` para usar `PostgreSQLUnitOfWork` con sesión real en lugar de `singleton_uow`
- [x] 6.2 Actualizar `backend/main.py` lifespan: antes del seed, llamar `alembic upgrade head` programáticamente (o `create_all_tables()` como fallback)

## 7. Infraestructura

- [x] 7.1 Re-habilitar servicio `db` en `docker-compose.yml` (postgres:15 con healthcheck y volumen)
- [x] 7.2 Actualizar `backend` en `docker-compose.yml`: agregar `depends_on: db (service_healthy)` y env vars de conexión
- [x] 7.3 Actualizar `Makefile`: re-agregar target `migrate` (`docker compose exec backend alembic upgrade head`)

## 8. Verificación

- [x] 8.1 `docker compose up --build` — los tres servicios arrancan sin errores
- [x] 8.2 `make migrate` — `alembic upgrade head` termina sin errores en BD limpia
- [x] 8.3 Verificar `GET /health` responde 200 y datos del admin están disponibles (login funciona)
- [x] 8.4 Crear un pedido, reiniciar el contenedor del backend, verificar que el pedido persiste
- [x] 8.5 Correr `make test` — tests unitarios pasan (usan InMemoryUoW, no deben cambiar)
