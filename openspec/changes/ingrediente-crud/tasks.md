## 1. Modelo y Migraciones

- [x] 1.1 Expandir `models/ingrediente.py` con: id (PK), nombre (unique), descripción, unidad_medida (enum), cantidad_stock, cantidad_minima, cantidad_reservada, is_active, created_at, updated_at, deleted_at, categoria_id (FK opcional)
- [ ] 1.2 Crear migration script SQL que cree tabla `ingredientes` con índices en (nombre, is_active, categoria_id, cantidad_stock)
- [ ] 1.3 Crear ENUM PostgreSQL para `unidad_medida` con valores: gramos, litros, unidades, kilos, mililitros
- [ ] 1.4 Crear seed script con ~30 ingredientes típicos (sal, azúcar, harina, leche, mantequilla, huevo, chocolate, canela, etc.)
- [ ] 1.5 Verificar que schema integra con ORM existente (SQLAlchemy, si corresponde)
- [ ] 1.6 Crear tabla `ingrediente_stock_history` para auditoría de cambios (id, ingrediente_id, admin_id, cantidad_anterior, cantidad_nueva, motivo, created_at)

## 2. Repository y Unit of Work

- [x] 2.1 Implementar `repositories/ingrediente_repository.py` con métodos:
  - `create(nombre: str, descripcion: str, unidad_medida: str, cantidad_stock: int, cantidad_minima: int, categoria_id: Optional[int]) -> Ingrediente`
  - `find_by_id(id: int) -> Optional[Ingrediente]`
  - `find_by_name(nombre: str) -> Optional[Ingrediente]`
  - `list_active(skip: int, limit: int, categoria_id: Optional[int], disponibles_solo: bool, alerta_stock_bajo: bool, unidad_medida: Optional[str], ordenar_por: str, orden: str) -> list[Ingrediente]`
  - `update(id: int, **kwargs) -> Ingrediente`
  - `soft_delete(id: int) -> None`
  - `puede_descontar(id: int, cantidad: int) -> bool`
  - `stock_disponible(id: int) -> int`
  - `buscar_por_nombre(q: str, skip: int, limit: int) -> list[Ingrediente]`
  - `find_all() -> list[Ingrediente]` (solo activos)
- [x] 2.2 Integrar IngredienteRepository en Unit of Work: actualizar `uow/uow.py` para incluir propiedad `ingredientes`
- [x] 2.3 Crear implementación en-memory de IngredienteRepository para testing
- [x] 2.4 Unit test IngredienteRepository: crear, leer, actualizar, soft_delete, find_by_name, puede_descontar, stock_disponible, buscar

## 3. Pydantic Schemas

- [x] 3.1 Crear `schemas/ingrediente_schema.py` con enums y requests:
  - `UnidadMedida` (enum): gramos, litros, unidades, kilos, mililitros
  - `IngredienteCreateRequest`: nombre (str, max 100), descripcion (str, max 500, opcional), unidad_medida (UnidadMedida), cantidad_stock (int, >= 0), cantidad_minima (int, >= 0), categoria_id (int, opcional)
  - `IngredienteUpdateRequest`: nombre (str, max 100, opcional), descripcion (str, max 500, opcional), cantidad_stock (int, >= 0, opcional), cantidad_minima (int, >= 0, opcional)
  - `IngredienteResponse`: id, nombre, descripcion, unidad_medida, cantidad_stock, cantidad_minima, stock_disponible, alerta_stock_bajo, categoria_id, is_active, created_at, updated_at
  - `IngredienteListResponse`: lista de IngredienteResponse + metadatos (total, skip, limit)
  - `StockHistoryResponse`: id, ingrediente_id, admin_id, cantidad_anterior, cantidad_nueva, motivo, created_at
- [x] 3.2 Agregar validadores Pydantic:
  - nombre: no vacío, no SQL injection, max 100 chars, unique
  - descripcion: max 500 chars, sanitizar caracteres especiales
  - cantidad_stock: no negativo, menor o igual a cantidad_minima permite
  - cantidad_minima: no negativo
  - unidad_medida: debe estar en enum
- [x] 3.3 Unit test schemas: inputs válidos e inválidos, edge cases (nombre vacío, muy largo, caracteres peligrosos, stock negativo)

## 4. Endpoints CRUD

- [x] 4.1 Crear `routers/ingredientes.py` con endpoint `POST /ingredientes`:
  - Requerir rol admin (@require_role("admin"))
  - Validar input con schema
  - Verificar nombre no duplicado con repo
  - Crear Ingrediente via repository
  - Devolver 201 + IngredienteResponse
- [x] 4.2 Crear endpoint `GET /ingredientes`:
  - Aceptar parámetros: skip (default 0), limit (default 20, max 100), categoria_id (opcional), disponibles_solo (default false), alerta_stock_bajo (default false), unidad_medida (opcional), ordenar_por (nombre|cantidad_stock|created_at), orden (asc|desc)
  - Listar ingredientes activos con filtros
  - Calcular stock_disponible y alerta_stock_bajo para cada uno
  - Devolver 200 + IngredienteListResponse
- [x] 4.3 Crear endpoint `GET /ingredientes/buscar?q=<query>`:
  - Buscar ingredientes por nombre (ILIKE)
  - Aceptar parámetros: q (obligatorio), skip, limit
  - Devolver 200 + IngredienteListResponse
- [x] 4.4 Crear endpoint `GET /ingredientes/{id}`:
  - Buscar ingrediente por id
  - Calcular stock_disponible y alerta_stock_bajo
  - Devolver 404 si no existe o está inactivo
  - Devolver 200 + IngredienteResponse
- [x] 4.5 Crear endpoint `PUT /ingredientes/{id}`:
  - Requerir rol admin
  - Validar input
  - Verificar nombre no duplicado (salvo si es el mismo nombre actual)
  - Registrar en historial de stock si cantidad_stock cambió
  - Actualizar via repository
  - Devolver 200 + IngredienteResponse
- [x] 4.6 Crear endpoint `DELETE /ingredientes/{id}`:
  - Requerir rol admin
  - Soft delete via repository
  - Devolver 204 No Content
- [x] 4.7 Crear endpoint `GET /ingredientes/{id}/historial-stock` (admin only):
  - Listar últimos 20 cambios de stock del ingrediente
  - Devolver 200 + array de StockHistoryResponse
- [x] 4.8 Integrar todos los endpoints en FastAPI app (actualizar main.py para incluir routers/ingredientes)

## 5. Lógica de Stock y Disponibilidad

- [x] 5.1 Implementar método `puede_descontar(ingrediente_id: int, cantidad: int) -> bool` que:
  - Valida que cantidad >= 0
  - Obtiene stock_disponible (stock - reservadas)
  - Retorna true si cantidad <= stock_disponible
  - Levanta excepción si ingrediente no existe o está inactivo
- [x] 5.2 Implementar método `calcular_alerta_stock_bajo(ingrediente_id: int) -> bool` que:
  - Obtiene ingrediente
  - Retorna true si cantidad_stock < cantidad_minima
- [x] 5.3 Unit test: puede_descontar con stock suficiente/insuficiente, cantidad negativa, ingrediente inactivo
- [x] 5.4 Unit test: alerta_stock_bajo con diferentes relaciones stock/minimo

## 6. Validaciones y Seguridad

- [ ] 6.1 Verificar rate limiting en POST /ingredientes (heredar de FastAPI app)
- [ ] 6.2 Verificar JWT middleware valida token en todas las rutas protegidas
- [ ] 6.3 Verificar @require_role("admin") rechaza non-admins con 403
- [ ] 6.4 Verificar unicidad de nombre a nivel BD (unique constraint)
- [ ] 6.5 Unit test: intentos de SQL injection, duplicados, access control, stock negativo
- [ ] 6.6 Unit test: edge cases (nombre de 1 char, 100 chars, descripción vacía vs omitida, unidades inválidas)
- [ ] 6.7 Validar que DELETE de ingrediente rechaza si está siendo usado en productos activos (o solo soft deletes)

## 7. Integration Tests

- [ ] 7.1 Integration test `POST /ingredientes`: crear válido → 201, inválido → 422, duplicado → 409, sin admin → 403
- [ ] 7.2 Integration test `GET /ingredientes`: listar con skip/limit, filtros (categoria, disponibles, alerta), ordenar
- [ ] 7.3 Integration test `GET /ingredientes/buscar`: búsqueda parcial, case-insensitive, sin resultados, query vacío → 400
- [ ] 7.4 Integration test `GET /ingredientes/{id}`: existe → 200, no existe → 404, inactivo → 404
- [ ] 7.5 Integration test `PUT /ingredientes/{id}`: actualizar válido → 200, duplicado → 409, sin admin → 403, registra historial
- [ ] 7.6 Integration test `DELETE /ingredientes/{id}`: soft delete → 204, ya inactivo → 204 (idempotencia), sin admin → 403
- [ ] 7.7 Integration test `GET /ingredientes/{id}/historial-stock`: admin solo, devuelve cambios anteriores
- [ ] 7.8 Integration test: listado sin ingredientes → array vacío; con ingredientes → todos activos
- [ ] 7.9 Integration test: stock_disponible se calcula correctamente con y sin reservas

## 8. Documentación y Limpieza

- [ ] 8.1 Documentar Ingrediente model en docstrings (purpose, fields, lifecycle, unidad_medida enum)
- [ ] 8.2 Documentar IngredienteRepository métodos (params, returns, raises)
- [ ] 8.3 Documentar métodos de stock: puede_descontar, stock_disponible, alerta_stock_bajo
- [ ] 8.4 Actualizar Swagger/OpenAPI con nuevos endpoints (debería auto-generarse en FastAPI)
- [ ] 8.5 Verificar que logs no exponen datos sensibles de ingredientes
- [ ] 8.6 Ejecutar linter (black, flake8) en archivos nuevos
- [ ] 8.7 Actualizar CHANGELOG.md o docs/ con resumen de cambios

## 9. Verificación Final

- [ ] 9.1 Correr todos los tests (unit + integration) con coverage >= 80%
- [ ] 9.2 Verificar BD seed cargó los ingredientes iniciales
- [ ] 9.3 Manual test: crear, editar, listar, borrar ingrediente via curl o Postman
- [ ] 9.4 Manual test: filtrar por categoría, disponibilidad, unidad_medida
- [ ] 9.5 Manual test: búsqueda por nombre (partial match)
- [ ] 9.6 Verificar error handling: requests malformadas, DB errors, edge cases
- [ ] 9.7 Verificar endpoints protegidos (GET /ingredientes es público, POST/PUT/DELETE son admin-only)
- [ ] 9.8 Verificar que stock_disponible se calcula correctamente en listados
- [ ] 9.9 Verificar alerta_stock_bajo funciona según cantidad_minima
