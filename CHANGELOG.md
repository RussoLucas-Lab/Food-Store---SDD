# CHANGELOG

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-05-07 - Ingrediente CRUD Implementation

### Added

#### Model Layer
- **Ingrediente Model** (`models/ingrediente.py`)
  - Full domain model with stock management properties
  - `UnidadMedida` enum with 5 units: gramos, litros, unidades, kilos, mililitros
  - Stock calculation properties: `stock_disponible` (stock - reservadas), `alerta_stock_bajo`
  - `puede_descontar(cantidad)` method for inventory validation
  - Soft-delete support via `is_active` flag and `deleted_at` timestamp
  - Auditable via `created_at` and `updated_at` timestamps

#### Repository Layer
- **InMemoryIngredienteRepository** (`repositories/ingrediente_repository.py`)
  - 12 public methods covering full CRUD lifecycle
  - Methods: create, find_by_id, find_by_name, list_active, buscar_por_nombre, update, soft_delete, puede_descontar, stock_disponible, find_all
  - Advanced filtering: categoria_id, disponibles_solo, alerta_stock_bajo, unidad_medida
  - Sorting: by id, nombre, cantidad_stock, created_at (asc/desc)
  - Pagination: skip/limit with configurable defaults
  - Name-indexed lookups for O(1) performance
  - Unique constraint validation on nombre (case-insensitive)

#### API Layer
- **Pydantic Schemas** (`backend/schemas/ingrediente_schema.py`)
  - `UnidadMedidaEnum` for type safety
  - `IngredienteCreateRequest` and `IngredienteUpdateRequest` with comprehensive validation
  - `IngredienteResponse` with calculated properties (stock_disponible, alerta_stock_bajo)
  - `IngredienteListResponse` with pagination metadata
  - `StockHistoryResponse` for audit trail
  - Validators for: nombre (1-100 chars, no SQL injection), descripcion (0-500 chars), stock (>= 0), enum values

- **7 REST Endpoints** (`backend/routers/ingredientes.py`)
  - `POST /ingredientes` - Create (admin-only, 201)
  - `GET /ingredientes` - List with filters & pagination (200)
  - `GET /ingredientes/buscar?q=...` - Search by nombre (200, 400 on missing q)
  - `GET /ingredientes/{id}` - Get detail (200, 404)
  - `PUT /ingredientes/{id}` - Update (admin-only, 200/404/409)
  - `DELETE /ingredientes/{id}` - Soft delete (admin-only, 204)
  - `GET /ingredientes/{id}/historial-stock` - Audit trail (admin-only, 200)
  - All endpoints integrated into FastAPI app with Swagger/OpenAPI support

#### Integration
- **Unit of Work Integration** (`uow/inmemory.py`, `uow/interfaces.py`)
  - `ingredientes` property in IUnitOfWork and InMemoryUnitOfWork
  - Follows repository pattern established in auth-roles and categoria-crud changes

#### Testing
- **Unit Tests** (34 tests in `test_ingrediente_repository.py`)
  - CRUD lifecycle: create, find, list, update, soft_delete
  - Search & filtering: by nombre, categoria, disponibilidad, stock alerts
  - Stock logic: puede_descontar, stock_disponible, alerta_stock_bajo
  - Edge cases: inactive ingredients, duplicate names, boundary conditions

- **Schema Tests** (16 tests in `test_ingrediente_schema.py`)
  - Validation: required fields, type checking, length constraints
  - Edge cases: min/max values, invalid enums, negative stock
  - Sanitization: SQL injection prevention, XSS protection

- **Integration Tests** (37 tests in `test_ingrediente_endpoints.py`)
  - Endpoint structure: response codes, field names, pagination
  - Validation: missing fields, invalid types, enum values, constraints
  - Filtering: all 4 filter types (categoria, disponibilidad, alerta, unidad)
  - Ordering: all 4 sort fields and both sort directions
  - Edge cases: boundary values, empty inputs, long strings

#### Total Coverage
- **87 passing tests** (100% success rate)
- Covers all 7 endpoints
- Validates all schemas and models
- Tests integration between layers

### Security
- Admin-only endpoints: POST, PUT, DELETE (role-based access control via `@require_role("admin")`)
- JWT middleware validates token in all protected routes
- Input validation prevents SQL injection and XSS
- Soft-delete preserves data integrity and enables auditing

### Database Ready
- Schema supports PostgreSQL migration with:
  - Table `ingredientes` with proper indexes (nombre, is_active, categoria_id)
  - ENUM type `unidad_medida` with 5 values
  - Soft-delete fields (is_active, deleted_at)
  - Optional audit table `ingrediente_stock_history`

### Architecture Decisions
- **Stock Calculation**: `stock_disponible` calculated dynamically (not persisted) to stay in sync with reservations
- **Soft-Delete**: Idempotent operation - multiple DELETE calls succeed without error
- **Search**: Partial match with case-insensitive comparison at repository layer (scalable to DB-level full-text search)
- **Pagination**: Defaults to 20 items, max 100 per request for performance
- **Enum**: Both model and schema define UnidadMedida to catch errors at schema validation before repo

### Notes for Next Change (producto-crud)
- Can now depend on ingredientes being queryable via UoW
- `puede_descontar()` method validates availability before product creation
- Stock history table ready for product deductions during fulfillment
- Admin and customer roles pre-configured in auth-roles change

---

## Previous Changes
- [0.2.0] - 2026-05-06 - Categoría CRUD (archived)
- [0.1.0] - 2026-05-06 - Authentication & Roles (archived)
