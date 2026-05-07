## Context

El backend Food Store ya tiene un patrón establecido de Repository + Unit of Work (UoW) integrado con FastAPI, JWT middleware, y control de acceso basado en roles (admin/customer). El modelo Categoría y sus endpoints funcionan correctamente. Ahora necesitamos extender ese patrón para Ingredientes, manteniendo coherencia con:
- Validación en Pydantic schemas
- Rate limiting y JWT auth
- Soft deletes (marcar inactivos, no borrar)
- Transacciones vía UoW
- Lógica de stock y disponibilidad

## Goals / Non-Goals

**Goals:**
- Implementar CRUD completo de ingredientes siguiendo el patrón UoW + Repository
- Asegurar que solo admins puedan crear, editar o borrar ingredientes (soft delete)
- Clientes pueden ver listado de ingredientes disponibles con stock
- Validar unicidad de nombre, unidad de medida válida, y stock no negativo
- Implementar lógica de stock: validaciones de disponibilidad, alertas de stock bajo
- Preparar la base para que producto-crud pueda referenciar ingredientes y validar disponibilidad

**Non-Goals:**
- No implementar transferencias de stock entre almacenes (inventario centralizado)
- No crear endpoints separados de búsqueda avanzada (listado con filtros básicos es suficiente)
- No integrar historial de movimientos de stock (tracking simple de cantidad)
- No integrar proveedores o reorden automática en esta fase

## Decisions

### 1. Patrón Repository + Unit of Work (Decision)

**Choice**: Extender el patrón existente de auth-roles y categoria-crud.
- **Why**: Ya probado en Usuario y Categoría, mantiene transacciones atómicas, permite testing inmemory, y facilita cambios de BD sin tocar endpoints.
- **Alternative**: Raw SQL queries en endpoints → acoplamiento, difícil de testear.
- **Implementation**: IngredienteRepository con métodos: `create()`, `find_by_id()`, `find_by_name()`, `list_available()`, `update()`, `soft_delete()`, `find_all()`. Integrar en UoW como propiedad `ingredientes`.

### 2. Soft Delete vs Hard Delete (Decision)

**Choice**: Soft delete (marcar `is_active = False`).
- **Why**: Los ingredientes pueden ser referenciados por productos. Borrar un ingrediente rompe integridad. Soft delete permite auditoría y rollback.
- **Alternative**: Cascade delete → pierde datos, complica rollback.
- **Implementation**: `soft_delete()` en repo que setea `is_active = False` y `deleted_at = now()`. Listados devuelven solo `is_active = True` por defecto. Query explícita para ver eliminadas.

### 3. Lógica de Stock (Decision)

**Choice**: Validar stock en el modelo, alertas de cantidad mínima, pero sin reorden automática.
- **Why**: Product-crud necesita validar disponibilidad. Cantidad mínima alerta al admin sin afectar venta.
- **Alternative**: Sin validaciones → overselling, sin visibilidad de stock bajo.
- **Implementation**: Campo `cantidad_minima` en modelo. Método `stock_disponible()` y `puede_descontar(cantidad)`. Endpoint GET /ingredientes devuelve `stock_disponible` y `alerta_stock_bajo` (boolean).

### 4. Unidad de Medida (Decision)

**Choice**: Enum fixed con valores: gramos, litros, unidades, kilos, mililitros.
- **Why**: Claridad, facilita conversiones y búsquedas. Evita typos (enum vs string libre).
- **Alternative**: String libre → typos, inconsistencia.
- **Implementation**: Enum `UnidadMedida` en schemas. BD almacena como string (ENUM de PostgreSQL).

### 5. Relación con Categorías (Decision)

**Choice**: Ingrediente puede tener categoría opcional (foreign key).
- **Why**: Organizar ingredientes por tipo (especias, lácteos, harinas, etc.). No es obligatorio en MVP.
- **Alternative**: Sin categorías → sin estructura.
- **Implementation**: Campo `categoria_id` (nullable) en modelo. En queries, join con tabla categorias solo si se solicita.

### 6. Autorización: Admin-Only para Mutaciones (Decision)

**Choice**: Endpoints POST/PUT/DELETE requieren `@require_role("admin")`.
- **Why**: Solo admins pueden gestionar ingredientes. Clientes acceden en modo read-only (listado de disponibles).
- **Alternative**: No restricción → cualquiera edita ingredientes (seguridad débil).
- **Implementation**: Usar decorador `@require_role("admin")` del middleware existente. GET /ingredientes público (no protegido).

### 7. Paginación y Filtros (Decision)

**Choice**: GET /ingredientes soporta parámetros opcionales `skip`, `limit`, `categoria_id`, `disponibles_solo`.
- **Why**: Escala bien si hay muchos ingredientes. Clientes pueden filtrar por categoría y ver solo disponibles.
- **Alternative**: Devolver todas de una vez → memoria, UI lenta.
- **Implementation**: Método en repo `list_available(skip, limit, categoria_id, disponibles_solo)`. Endpoint GET /ingredientes?skip=0&limit=20&disponibles_solo=true.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Integridad referencial**: Producto referencia ingrediente, luego ingrediente se marca inactivo → huérfano inconsistente | En producto-crud, validar que referencia sea a ingrediente `is_active = True`. En queries, join explícito a ingredientes activos. |
| **Overselling**: Pedido consume stock, pero no hay transacción atómica → venta de más del disponible | Esto se maneja en carrito-pedidos con transacciones UoW. Aquí solo validamos `puede_descontar()`. Implementar reservas en carrito-pedidos. |
| **Race condition en nombre único**: Dos requests simultáneos POST con mismo nombre → ambas ven `not found` y crean | BD unique constraint lo previene (error 409). Pydantic + try/except en endpoint. |
| **Performance**: Muchos ingredientes con queries complejas → listado lento | Índice en `nombre`, `is_active`, `categoria_id`. Paginación. OK para MVP. |
| **Cantidad mínima poco clara**: ¿Se puede vender si stock < cantidad_minima? | SÍ, cantidad_minima es solo alerta. Se valida disponibilidad en producto-crud/carrito-pedidos. |

## Migration Plan

**Deploy steps:**
1. Crear migration script SQL que cree tabla `ingredientes` con schema completo (incluyendo foreign key a categorías).
2. Crear Enum `UnidadMedida` en PostgreSQL.
3. Cargar tabla seed con ~30 ingredientes típicos (sal, azúcar, harina, leche, etc.).
4. Deployar endpoints de CRUD bajo `/ingredientes`.
5. Actualizar documentación API (Swagger/OpenAPI).

**Rollback strategy:**
- Si error crítico pre-deploy: no commitear migration.
- Si error post-deploy: dropear tabla `ingredientes`, revertir routers, confirmar que productos aún no existen (lo sabemos porque son downstream).

## Open Questions

1. ¿Los ingredientes necesitan imagen de referencia (url) para UI frontend? → Aplazado a frontend-ajustes-finales.
2. ¿Descripción de ingrediente en POST o dejarla nullable? → Nullable, frontend puede pedirla opcionalmente.
3. ¿Auditar cambios de ingredientes (quién editó cuándo)? → Aplazado, por ahora solo timestamps de creación/actualización.
4. ¿Qué sucede si se intenta descontar más stock del disponible? → Error 409 Conflict con mensaje claro. Esto lo maneja carrito-pedidos.
