## 1. Modelo y Migraciones

- [x] 1.1 Expandir `models/categoria.py` con: id (PK), nombre (unique), descripción, is_active, created_at, updated_at, deleted_at
- [x] 1.2 Crear migration script SQL que cree tabla `categorias` con índices en (nombre, is_active)
- [x] 1.3 Crear seed script con ~10 categorías típicas (Bebidas, Postres, Hamburguesas, Ensaladas, etc.)
- [x] 1.4 Verificar que schema integra con ORM existente (SQLAlchemy, si corresponde)

## 2. Repository y Unit of Work

- [x] 2.1 Implementar `repositories/categoria_repository.py` con métodos:
  - `create(nombre: str, descripcion: str) -> Categoria`
  - `find_by_id(id: int) -> Optional[Categoria]`
  - `find_by_name(nombre: str) -> Optional[Categoria]`
  - `list_active(skip: int, limit: int, sort_by: str, include_inactive: bool) -> list[Categoria]`
  - `update(id: int, nombre: str, descripcion: str) -> Categoria`
  - `soft_delete(id: int) -> None`
  - `find_all() -> list[Categoria]` (solo activas)
- [x] 2.2 Integrar CategoriaRepository en Unit of Work: actualizar `uow/uow.py` para incluir propiedad `categorias`
- [x] 2.3 Crear implementación en-memory de CategoriaRepository para testing
- [x] 2.4 Unit test CategoriaRepository: crear, leer, actualizar, soft_delete, find_by_name con duplicados

## 3. Pydantic Schemas

- [x] 3.1 Crear `schemas/categoria_schema.py` con:
  - `CategoriaCreateRequest`: nombre (str, max 100), descripcion (str, max 500, opcional)
  - `CategoriaUpdateRequest`: nombre (str, max 100, opcional), descripcion (str, max 500, opcional)
  - `CategoriaResponse`: id, nombre, descripcion, is_active, created_at, updated_at
  - `CategoriaListResponse`: lista de CategoriaResponse + metadatos (total, skip, limit)
- [x] 3.2 Agregar validadores Pydantic:
  - nombre: no vacío, no SQL injection, max 100 chars
  - descripcion: max 500 chars, sanitizar caracteres especiales
  - Email-like validación (si aplica), unicidad simulada
- [x] 3.3 Unit test schemas: inputs válidos e inválidos, edge cases (nombre vacío, muy largo, caracteres peligrosos)

## 4. Endpoints CRUD

- [x] 4.1 Crear `routers/categorias.py` con endpoint `POST /categorias`:
  - Requerir rol admin (@require_role("admin"))
  - Validar input con schema
  - Verificar nombre no duplicado con repo
  - Crear Categoría via repository
  - Devolver 201 + CategoriaResponse
- [x] 4.2 Crear endpoint `GET /categorias`:
  - Aceptar parámetros: skip (default 0), limit (default 20, max 100), sort (id, nombre, created_at), include_inactive (admin only)
  - Listar categorías activas (o todas si admin y include_inactive=true)
  - Devolver 200 + CategoriaListResponse
- [x] 4.3 Crear endpoint `GET /categorias/{id}`:
  - Buscar categoría por id
  - Devolver 404 si no existe o está inactiva
  - Devolver 200 + CategoriaResponse
- [x] 4.4 Crear endpoint `PUT /categorias/{id}`:
  - Requerir rol admin
  - Validar input
  - Verificar nombre no duplicado (salvo si es el mismo nombre actual)
  - Actualizar via repository
  - Devolver 200 + CategoriaResponse
- [x] 4.5 Crear endpoint `DELETE /categorias/{id}`:
  - Requerir rol admin
  - Soft delete via repository
  - Devolver 204 No Content
- [x] 4.6 Integrar todos los endpoints en FastAPI app (actualizar main.py para incluir routers/categorias)

## 5. Validaciones y Seguridad

- [x] 5.1 Verificar rate limiting en POST /categorias (heredar de FastAPI app)
- [x] 5.2 Verificar JWT middleware valida token en todas las rutas protegidas
- [x] 5.3 Verificar @require_role("admin") rechaza non-admins con 403
- [x] 5.4 Verificar unicidad de nombre a nivel BD (unique constraint)
- [x] 5.5 Unit test: intentos de SQL injection, duplicados, access control
- [x] 5.6 Unit test: edge cases (nombre de 1 char, 100 chars, descripción vacía vs omitida)

## 6. Integration Tests

- [x] 6.1 Integration test `POST /categorias`: crear válida → 201, inválida → 422, duplicada → 409, sin admin → 403
- [x] 6.2 Integration test `GET /categorias`: listar con skip/limit, filtros, sorting
- [x] 6.3 Integration test `GET /categorias/{id}`: existe → 200, no existe → 404, inactiva → 404
- [x] 6.4 Integration test `PUT /categorias/{id}`: actualizar válida → 200, duplicada → 409, sin admin → 403
- [x] 6.5 Integration test `DELETE /categorias/{id}`: soft delete → 204, ya inactiva → 204 (idempotencia), sin admin → 403
- [x] 6.6 Integration test: listado sin categorías → array vacío; con categorías → todos activos

## 7. Documentación y Limpieza

- [x] 7.1 Documentar Categoria model en docstrings (purpose, fields, lifecycle)
- [x] 7.2 Documentar CategoriaRepository métodos (params, returns, raises)
- [x] 7.3 Actualizar Swagger/OpenAPI con nuevos endpoints (debería auto-generarse en FastAPI)
- [x] 7.4 Verificar que logs no exponen datos sensibles de categorías
- [ ] 7.5 Ejecutar linter (black, flake8) en archivos nuevos
- [ ] 7.6 Actualizar CHANGELOG.md o docs/ con resumen de cambios

## 8. Verificación Final

- [x] 8.1 Correr todos los tests (unit + integration) con coverage >= 80%
- [ ] 8.2 Verificar BD seed cargó las categorías iniciales
- [ ] 8.3 Manual test: crear, editar, listar, borrar categoría via curl o Postman
- [ ] 8.4 Verificar error handling: requests malformadas, DB errors, edge cases
- [ ] 8.5 Verificar endpoints protegidos (GET /categorias es público, POST/PUT/DELETE son admin-only)
