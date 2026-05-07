# Specifications: Refactor Categoría e Ingrediente para Service Layer

## 1. CategoryService Requirements

### 1.1 Create Categoria
**Requirement**: CategoryService.create_categoria(nombre, descripcion) creates a new category with validation

**Scenarios**:
- ✅ Crear categoría con nombre y descripción válidos → retorna DTO con id, nombre, descripcion, status='active'
- ❌ Nombre vacío → ValueError("Nombre requerido")
- ❌ Nombre duplicado → ValueError("Categoría '{nombre}' ya existe")
- ❌ Descripción > 500 chars → ValueError("Descripción no puede exceder 500 caracteres")

**Data Contract**:
```python
# Input
nombre: str (1-100 chars, required)
descripcion: str (0-500 chars, optional, default "")

# Output
{
  "id": int,
  "nombre": str,
  "descripcion": str,
  "status": "active",
  "created_at": datetime,
  "updated_at": datetime
}

# Exceptions
ValueError("Nombre requerido")  # → router maps to 400
ValueError("Categoría '{nombre}' ya existe")  # → router maps to 409
ValueError("Descripción no puede exceder...")  # → router maps to 400
```

### 1.2 Update Categoria
**Requirement**: CategoryService.update_categoria(id, nombre, descripcion) updates an existing category

**Scenarios**:
- ✅ Actualizar nombre y descripción válidos → retorna DTO actualizado
- ❌ ID no existe → ValueError("Categoría {id} no existe") [404]
- ❌ Nombre duplicado (otro que no sea self) → ValueError("Nombre '{nombre}' ya está en uso") [409]
- ❌ Nombre vacío → ValueError("Nombre requerido") [400]

### 1.3 Delete Categoria
**Requirement**: CategoryService.delete_categoria(id) soft-deletes a category if not in use

**Scenarios**:
- ✅ Categoría no está en uso → status='inactive', retorna DTO
- ❌ ID no existe → ValueError("Categoría {id} no existe") [404]
- ❌ Categoría en uso por productos activos → ValueError("Categoría '{nombre}' está en uso por productos activos") [409]

**Important**: Check `uow.productos.count_by_category(id)` — must return 0 for delete to succeed

### 1.4 Get Categoria
**Requirement**: CategoryService.get_categoria(id) retrieves a single category

**Scenarios**:
- ✅ ID existe → retorna DTO
- ❌ ID no existe → ValueError("Categoría {id} no existe") [404]

### 1.5 List Categorias
**Requirement**: CategoryService.list_categorias(skip, limit, search) retrieves categories with pagination

**Scenarios**:
- ✅ Sin filtros → retorna lista paginada (skip=0, limit=10)
- ✅ Con search → busca en nombre/descripción (case-insensitive)
- ✅ Con skip/limit → respeta paginación
- ✅ Lista vacía si no hay resultados → []

---

## 2. IngredientService Requirements

### 2.1 Create Ingrediente
**Requirement**: IngredientService.create_ingrediente(...) creates a new ingredient with validation

**Scenarios**:
- ✅ Crear con nombre, unidad_medida, stock, cantidad_minima válidos → retorna DTO
- ❌ Nombre vacío → ValueError("Nombre requerido")
- ❌ Nombre duplicado → ValueError("Ingrediente '{nombre}' ya existe")
- ❌ Unidad medida inválida → ValueError("Unidad medida debe ser: gramos, litros, unidades, kilos, mililitros")
- ❌ cantidad_stock < 0 → ValueError("Stock no puede ser negativo")
- ❌ cantidad_minima < 0 → ValueError("Cantidad mínima no puede ser negativa")

**Data Contract**:
```python
# Input
nombre: str (1-100 chars, required)
unidad_medida: str (gramos|litros|unidades|kilos|mililitros, required)
cantidad_stock: float (>= 0, required)
cantidad_minima: float (>= 0, required)
descripcion: str (0-500 chars, optional)
categoria_id: int (optional, FK to categorias)

# Output
{
  "id": int,
  "nombre": str,
  "unidad_medida": str,
  "cantidad_stock": float,
  "cantidad_minima": float,
  "descripcion": str,
  "status": "active",
  "categoria_id": int | null,
  "created_at": datetime,
  "updated_at": datetime
}
```

### 2.2 Update Ingrediente
**Requirement**: IngredientService.update_ingrediente(id, ...) updates an ingredient

**Scenarios**:
- ✅ Actualizar stock, cantidad_minima, descripción → retorna DTO
- ❌ ID no existe → ValueError("Ingrediente {id} no existe") [404]
- ❌ Nombre duplicado (otro que no sea self) → ValueError("Nombre ya está en uso") [409]
- ❌ cantidad_stock < 0 → ValueError("Stock no puede ser negativo") [400]

### 2.3 Delete Ingrediente
**Requirement**: IngredientService.delete_ingrediente(id) soft-deletes if not in use

**Scenarios**:
- ✅ No está en uso → status='inactive', retorna DTO
- ❌ ID no existe → ValueError("Ingrediente {id} no existe") [404]
- ❌ En uso por productos activos → ValueError("Ingrediente '{nombre}' está en uso por productos activos") [409]

**Important**: Check `uow.productos.count_by_ingredient(id)` — must return 0

### 2.4 Get Ingrediente
**Requirement**: IngredientService.get_ingrediente(id) retrieves a single ingredient

**Scenarios**:
- ✅ ID existe → retorna DTO
- ❌ ID no existe → ValueError("Ingrediente {id} no existe") [404]

### 2.5 List Ingredientes
**Requirement**: IngredientService.list_ingredientes(skip, limit, search, unidad_medida, categoria_id) retrieves with filters

**Scenarios**:
- ✅ Sin filtros → retorna lista paginada
- ✅ Con search → busca en nombre/descripción
- ✅ Con unidad_medida → filtra por tipo
- ✅ Con categoria_id → filtra por categoría
- ✅ Combinar filtros → AND logic

### 2.6 Get Stock History
**Requirement**: IngredientService.get_stock_history(id) retrieves stock changes

**Scenarios**:
- ✅ ID existe → retorna lista de cambios ordenados por fecha DESC
- ❌ ID no existe → ValueError("Ingrediente {id} no existe") [404]
- ✅ Sin cambios → []

**Data Contract**:
```python
[
  {
    "id": int,
    "ingrediente_id": int,
    "cantidad_anterior": float,
    "cantidad_nueva": float,
    "motivo": str,  # "purchase", "use", "adjustment"
    "timestamp": datetime
  },
  ...
]
```

---

## 3. Exception Mapping

**CategoryService/IngredientService** raise ValueError with specific messages.  
**Routers** catch and map to HTTP:

| Exception | Message Pattern | HTTP Status |
|-----------|-----------------|------------|
| ValueError | "ya existe" | 409 Conflict |
| ValueError | "no existe" | 404 Not Found |
| ValueError | "en uso" | 409 Conflict |
| ValueError | "Nombre requerido" | 400 Bad Request |
| ValueError | other | 400 Bad Request |
| Exception | * | 500 Internal Server Error |

---

## 4. Integration Points

### 4.1 UoW Dependencies
Services receive `uow: IUnitOfWork` in constructor:
- `uow.categorias` — CategoryRepository
- `uow.ingredientes` — IngredientRepository
- `uow.productos` — ProductRepository (for count_by_category, count_by_ingredient)

### 4.2 Routers
- Import service from backend/services/
- Instantiate with UoW in route module
- Wrap calls in try/except ValueError
- Map ValueError to HTTPException(status, detail)

### 4.3 No Database Changes
- All repositories remain identical
- All SQL migrations remain unchanged
- Services are purely business logic layer

---

## 5. Testing Strategy

### 5.1 Unit Tests (test_categoria_service.py)
```python
def test_create_categoria_valid():
    # Mock UoW + repositories
    # Call service.create_categoria()
    # Assert returns dict with id, nombre, status='active'

def test_create_categoria_duplicate_name():
    # Setup: mock repo returns existing categoria
    # Call service.create_categoria() with duplicate name
    # Assert raises ValueError("ya existe")

def test_delete_categoria_in_use():
    # Setup: mock uow.productos.count_by_category() returns > 0
    # Call service.delete_categoria()
    # Assert raises ValueError("en uso")
```

### 5.2 Integration Tests (test_categoria_endpoints.py)
```python
def test_create_categoria_integration():
    # Use real UoW (in-memory)
    # POST /categorias with valid payload
    # Assert 201, response has id/nombre/status

def test_create_categoria_conflict():
    # Create categoria 1
    # POST /categorias with duplicate nombre
    # Assert 409 Conflict
```

### Coverage Target
- CategoryService: > 90% coverage
- IngredientService: > 90% coverage
- Router exception mapping: > 80% coverage
