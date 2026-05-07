## Context

El backend Food Store ya tiene un patrón establecido de Repository + Unit of Work (UoW) integrado con FastAPI, JWT middleware, y control de acceso basado en roles (admin/customer). El modelo Usuario y los endpoints de autenticación funcionan correctamente. Ahora necesitamos extender ese patrón para Categorías, manteniendo coherencia con:
- Validación en Pydantic schemas
- Rate limiting y JWT auth
- Soft deletes (marcar inactivos, no borrar)
- Transacciones vía UoW

## Goals / Non-Goals

**Goals:**
- Implementar CRUD completo de categorías siguiendo el patrón UoW + Repository
- Asegurar que solo admins puedan crear, editar o borrar categorías (soft delete)
- Clientes pueden ver listado de categorías activas
- Validar unicidad de nombre, formato, y evitar categorías huérfanas
- Preparar la base para que ingrediente-crud y producto-crud puedan referenciar categorías sin romper

**Non-Goals:**
- No implementar jerarquía de categorías (padre-hijo) en esta fase
- No crear endpoints separados de búsqueda avanzada (listado con filtros básicos es suficiente)
- No integrar etiquetas o tags adicionales a categorías

## Decisions

### 1. Patrón Repository + Unit of Work (Decision)

**Choice**: Extender el patrón existente de auth-roles.
- **Why**: Ya probado en Usuario, mantiene transacciones atómicas, permite testing inmemory, y facilita cambios de BD sin tocar endpoints.
- **Alternative**: Raw SQL queries en endpoints → acoplamiento, difícil de testear.
- **Implementation**: CategoriaRepository con métodos: `create()`, `find_by_id()`, `find_by_name()`, `list_active()`, `update()`, `soft_delete()`, `find_all()`. Integrar en UoW como propiedad `categorias`.

### 2. Soft Delete vs Hard Delete (Decision)

**Choice**: Soft delete (marcar `is_active = False`).
- **Why**: Las categorías pueden ser referenciadas por productos e ingredientes. Borrar una categoría rompe integridad. Soft delete permite auditoría y rollback.
- **Alternative**: Cascade delete → pierde datos, complica rollback.
- **Implementation**: `soft_delete()` en repo que setea `is_active = False` y `deleted_at = now()`. Listados devuelven solo `is_active = True` por defecto. Query explícita para ver eliminadas.

### 3. Validación de Unicidad (Decision)

**Choice**: Nombre único a nivel BD + validación Pydantic.
- **Why**: Previene duplicados en BD, Pydantic evita requests malformadas. Dos capas de validación.
- **Alternative**: Solo Pydantic → race condition en requests concurrentes.
- **Implementation**: Unique constraint en tabla `categorias.nombre`. En POST/PUT, verificar con `find_by_name()` antes de crear.

### 4. Autorización: Admin-Only para Mutaciones (Decision)

**Choice**: Endpoints POST/PUT/DELETE requieren `@require_role("admin")`.
- **Why**: Solo admins pueden gestionar categorías. Clientes acceden en modo read-only.
- **Alternative**: No restricción → cualquiera edita categorías (seguridad débil).
- **Implementation**: Usar decorador `@require_role("admin")` del middleware existente. GET /categorias público (no protegido).

### 5. Paginación y Filtros (Decision)

**Choice**: GET /categorias soporta parámetros opcionales `skip` y `limit` + filtro por `is_active`.
- **Why**: Escala bien si hay muchas categorías. Clientes pueden hacer paginación.
- **Alternative**: Devolver todas de una vez → memoria, UI lenta.
- **Implementation**: Método en repo `list_active(skip: int, limit: int)`. Endpoint GET /categorias?skip=0&limit=20.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Integridad referencial**: Producto/Ingrediente referencia categoría, luego categoría se marca inactiva → huérfano inconsistente | En ingrediente-crud y producto-crud, validar que referencia sea a categoría `is_active = True`. En queries, join explícito a categorías activas. |
| **Eliminación por accidente**: Admin borra categoría sin darse cuenta → no hay recuperación automática | Soft delete garantiza que datos existen. Implementar endpoint `/admin/categorias/restore/{id}` en fase siguiente. Por ahora, OK. |
| **Race condition en nombre único**: Dos requests simultáneos POST con mismo nombre → ambas ven `not found` y crean | BD unique constraint lo previene (error 409). Pydantic + try/except en endpoint. |
| **Performance**: Muchas categorías → listado lento | Índice en `nombre` y `is_active`. Paginación. OK para MVP. |

## Migration Plan

**Deploy steps:**
1. Crear migration script SQL que cree tabla `categorias` con schema completo.
2. Cargar tabla seed con ~10 categorías típicas (Bebidas, Postres, Hamburguesas, etc.).
3. Deployar endpoints de CRUD bajo `/categorias`.
4. Actualizar documentación API (Swagger/OpenAPI).

**Rollback strategy:**
- Si error crítico pre-deploy: no commitear migration.
- Si error post-deploy: dropear tabla `categorias`, revertir routers, confirmar que productos/ingredientes aún no existen (lo sabemos porque son downstream).

## Open Questions

1. ¿Las categorías necesitan un `display_order` o `icon_url` para UI frontend? → Aplazado a frontend-ajustes-finales.
2. ¿Describir categoría (descripción larga) en POST o dejarla nullable? → Nullable, frontend puede pedirla opcionalmente.
3. ¿Auditar cambios de categorías (quién editó cuándo)? → Aplazado, por ahora solo timestamps de creación/actualización.
