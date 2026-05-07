# Design: Refactor Categoría e Ingrediente para Service Layer

## Context

**Current State**:
```
Router (categorias.py, ingredientes.py)
  ├─ Validation logic
  ├─ Repository calls
  ├─ Error handling
  └─ HTTP response formatting
```

**Target State**:
```
Router (HTTP/Auth concerns only)
  │
  ├─ CategoryService (business logic)
  │   ├─ Validation
  │   ├─ Repository coordination
  │   └─ Exception raising (ValueError)
  │
  └─ IngredientService (business logic)
      ├─ Validation
      ├─ Repository coordination
      └─ Exception raising (ValueError)
```

---

## Goals

1. **Separation of Concerns**: HTTP concerns (FastAPI) separate from business logic
2. **Testability**: CategoryService/IngredientService can be unit tested without mocking FastAPI
3. **Consistency**: Match Producto's architecture (Repository + UoW + Service Layer)
4. **Reusability**: Services can be called from CLI, scripts, or other routers

---

## Technical Approach

### 1. CategoryService Design

**File**: `backend/services/categoria_service.py`

```python
class CategoryService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
    
    def create_categoria(self, nombre: str, descripcion: str = "") -> dict:
        """
        Crear categoría.
        
        Raises:
            ValueError: Si nombre ya existe (409 Conflict en router)
            ValueError: Si nombre vacío (400 Bad Request en router)
        """
        if not nombre or not nombre.strip():
            raise ValueError("Nombre requerido")
        
        if self.uow.categorias.find_by_name(nombre):
            raise ValueError(f"Categoría '{nombre}' ya existe")
        
        cat = self.uow.categorias.create(nombre, descripcion)
        self.uow.commit()
        return cat.to_dict()
    
    def update_categoria(self, id: int, nombre: str, descripcion: str) -> dict:
        """Actualizar categoría. Validar nombre único (excepto self)."""
        if not nombre or not nombre.strip():
            raise ValueError("Nombre requerido")
        
        cat = self.uow.categorias.get_by_id(id)
        if not cat:
            raise ValueError(f"Categoría {id} no existe")
        
        # Check nombre único (excepto self)
        existing = self.uow.categorias.find_by_name(nombre)
        if existing and existing.id != id:
            raise ValueError(f"Nombre '{nombre}' ya está en uso")
        
        cat.nombre = nombre
        cat.descripcion = descripcion
        self.uow.categorias.update(cat)
        self.uow.commit()
        return cat.to_dict()
    
    def delete_categoria(self, id: int) -> dict:
        """
        Soft-delete categoría.
        
        Raises:
            ValueError: Si categoría no existe (404)
            ValueError: Si está en uso por productos activos (409)
        """
        cat = self.uow.categorias.get_by_id(id)
        if not cat:
            raise ValueError(f"Categoría {id} no existe")
        
        # Check if in use by active products
        if self.uow.productos.count_by_category(id):
            raise ValueError(f"Categoría '{cat.nombre}' está en uso por productos activos")
        
        cat.status = "inactive"
        self.uow.categorias.update(cat)
        self.uow.commit()
        return cat.to_dict()
    
    def get_categoria(self, id: int) -> dict:
        """Obtener categoría por ID."""
        cat = self.uow.categorias.get_by_id(id)
        if not cat:
            raise ValueError(f"Categoría {id} no existe")
        return cat.to_dict()
    
    def list_categorias(self, skip: int = 0, limit: int = 10, search: str = None) -> list:
        """Listar categorías con paginación y búsqueda opcional."""
        return self.uow.categorias.list_all(skip=skip, limit=limit, search=search)
```

### 2. IngredientService Design

Similar a CategoryService:

```python
class IngredientService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
    
    def create_ingrediente(self, nombre: str, unidad_medida: str, 
                          cantidad_stock: float, cantidad_minima: float,
                          descripcion: str = "", categoria_id: int = None) -> dict:
        """Crear ingrediente con validaciones."""
        # Validar nombre único, stock >= 0, unidad válida, etc.
        # Raise ValueError si falla
        ...
    
    def delete_ingrediente(self, id: int) -> dict:
        """
        Soft-delete ingrediente.
        
        Raises ValueError si está en uso por productos activos (409).
        """
        # Check self.uow.productos.count_by_ingredient(id)
        ...
    
    def get_stock_history(self, id: int) -> list:
        """Obtener historial de cambios de stock para el ingrediente."""
        # Retorna lista de cambios (si se implementa tracking)
        ...
```

### 3. Router Refactoring

**categorias.py** antes:
```python
@router.post("", response_model=CategoriaResponse, status_code=201)
def create_categoria(req: CategoriaCreateRequest, user_id: int = Depends(require_role("admin"))):
    try:
        if uow.categorias.find_by_name(req.nombre):
            raise HTTPException(status_code=409, detail="...")
        categoria = uow.categorias.create(req.nombre, req.descripcion or "")
        uow.commit()
        return CategoriaResponse(**categoria.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

**categorias.py** después:
```python
categoria_service = CategoryService(uow)

@router.post("", response_model=CategoriaResponse, status_code=201)
def create_categoria(req: CategoriaCreateRequest, user_id: int = Depends(require_role("admin"))):
    try:
        result = categoria_service.create_categoria(req.nombre, req.descripcion or "")
        return CategoriaResponse(**result)
    except ValueError as e:
        # Map ValueError to appropriate HTTP status
        if "ya existe" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno")
```

---

## Exception Mapping

| Service Exception | HTTP Status | Meaning |
|-------------------|------------|---------|
| ValueError + "ya existe" | 409 | Conflict (duplicate) |
| ValueError + "no existe" | 404 | Not found |
| ValueError + "en uso" | 409 | Conflict (integrity constraint) |
| ValueError + other | 400 | Bad request |
| Other Exception | 500 | Internal server error |

---

## Migration Path

### Phase 1: Create Services (no router changes)
- Write CategoryService + IngredientService
- Test with unit tests (mock UoW)
- Test with integration tests (real UoW)

### Phase 2: Refactor Routers
- Update categorias.py to use CategoryService
- Update ingredientes.py to use IngredientService
- Run existing tests (endpoints should work identically)
- Add new unit tests for services

### Phase 3: Verification
- All endpoints return identical responses
- Error codes identical (400, 404, 409, 500)
- Coverage > 80%
- No breaking changes

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Breaking Changes** | High | Use integration tests to verify API contracts before/after |
| **Logic Loss** | Medium | Line-by-line code review during refactoring |
| **Performance** | Low | No extra queries added |

---

## Files Affected

| File | Change | Lines |
|------|--------|-------|
| `backend/services/categoria_service.py` | NEW | ~120 |
| `backend/services/ingrediente_service.py` | NEW | ~150 |
| `backend/routers/categorias.py` | MODIFIED | -80, +20 |
| `backend/routers/ingredientes.py` | MODIFIED | -120, +30 |
| `uow/interfaces.py` | NO CHANGE | — |
| `repositories/categoria_repository.py` | NO CHANGE | — |
| `repositories/ingrediente_repository.py` | NO CHANGE | — |

---

## Success Criteria

✅ Services created and unit tested
✅ Routers refactored (lógica → service)
✅ All endpoints identical behavior
✅ Integration tests pass
✅ Coverage > 80%
