# Proposal: Refactor Categoría e Ingrediente para Service Layer

## Why

**Architectural Inconsistency**: Producto (Change 6) implementó correctamente el patrón **Repository + Unit of Work + Service Layer**, pero Categoría e Ingrediente tienen toda la lógica de negocio **directamente en los routers** sin una Service Layer intermedia.

**Deuda Técnica**: 
- Lógica de validación mezclada con HTTP concerns (FastAPI routers)
- Difícil de testear unitariamente
- Imposible reutilizar lógica desde otros contextos
- Inconsistencia con el patrón establecido en Producto

**Beneficio**: 
- Código más testeable (unit tests sin mocks de FastAPI)
- Separación clara de responsabilidades
- Reutilización de servicios en otros routers/contextos
- Codebase más limpio y mantenible

---

## What Changes

### 1. CategoryService
Extraer lógica de `backend/routers/categorias.py` a nuevo `backend/services/categoria_service.py`:
- `create_categoria(nombre, descripcion)` → valida nombre único, crea, retorna DTO
- `update_categoria(id, nombre, descripcion)` → valida nombre único (excepto self), actualiza
- `delete_categoria(id)` → valida no esté en uso por productos, soft-delete
- `get_categoria(id)` → retorna DTO
- `list_categorias(skip, limit, search)` → retorna lista con paginación
- Recibe UoW en constructor para acceso a repositorios
- Lanza excepciones de negocio (ValueError) que el router mapea a HTTP

### 2. IngredientService
Extraer lógica de `backend/routers/ingredientes.py` a nuevo `backend/services/ingrediente_service.py`:
- `create_ingrediente(nombre, unidad_medida, cantidad_stock, cantidad_minima, descripcion, categoria_id)`
- `update_ingrediente(id, ...)`
- `delete_ingrediente(id)` → valida no esté en uso por productos
- `get_ingrediente(id)`
- `list_ingredientes(skip, limit, search, unidad_medida, categoria_id)`
- `get_stock_history(id)` → retorna historial de cambios de stock
- Similar a CategoryService: recibe UoW, lanza ValueError

### 3. Router Refactoring
Simplificar `categorias.py` y `ingredientes.py`:
- Remove business logic
- Call CategoryService / IngredientService methods
- Map exceptions: ValueError → HTTPException(400 or 409)
- Keep only HTTP/FastAPI concerns (routing, authorization, response formatting)

### 4. No Database Changes
- Repositorios permanecen igual
- Modelos permanecen igual
- Migrations permanecen igual
- Solo reorganización de código

---

## Capabilities Enabled

✅ **Testeable**: Unit tests para CategoryService + IngredientService sin mocks de FastAPI
✅ **Reutilizable**: Otros routers pueden usar CategoryService / IngredientService
✅ **Consistente**: Ahora Producto, Categoría, Ingrediente siguen el mismo patrón
✅ **Mantenible**: Lógica de negocio centralizada, fácil de modificar

---

## Impact

| Area | Change | Risk |
|------|--------|------|
| **API** | Sin cambios externos (endpoints, contracts idénticos) | 0% |
| **Database** | Sin cambios | 0% |
| **Tests** | Nuevos tests unitarios para services | +40 tests |
| **Codebase** | +2 files (services), -100+ lines en routers, +50 lines en routers | Neutral |

---

## Success Criteria

- [ ] CategoryService creado y testeado (unit + integration)
- [ ] IngredientService creado y testeado (unit + integration)
- [ ] categorias.py refactorizado (lógica → service)
- [ ] ingredientes.py refactorizado (lógica → service)
- [ ] Todos los endpoints siguen funcionando (POST/GET/PUT/DELETE)
- [ ] Validaciones idénticas (409 Conflict, 400 Bad Request, 404 Not Found)
- [ ] Coverage > 80% para ambos services
- [ ] Commit: "refactor: extract CategoryService and IngredientService from routers"
