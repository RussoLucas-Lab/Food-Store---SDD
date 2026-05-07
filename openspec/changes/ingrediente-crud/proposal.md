## Why

Food Store necesita un sistema de gestión de ingredientes para construir productos compuestos y controlar el inventario. Los ingredientes son la base fundamental para definir recetas y productos, y son requisito previo para el CRUD de productos. Sin un CRUD sólido de ingredientes con lógica de stock, no es posible gestionar productos que se compon de múltiples insumos, ni aplicar validaciones de disponibilidad en pedidos.

## What Changes

- **Nuevo modelo Ingrediente** con nombre, descripción, unidad de medida, cantidad en stock, cantidad mínima, estado activo/inactivo, timestamps
- **Endpoints CRUD**: `POST /ingredientes` (crear), `GET /ingredientes` (listar con filtros), `GET /ingredientes/{id}` (detalle), `PUT /ingredientes/{id}` (actualizar), `DELETE /ingredientes/{id}` (marcar como inactivo)
- **Validaciones**: nombre único, no vacío, longitud máxima; unidad de medida válida; stock no negativo; cantidad mínima no negativa
- **Repository de Ingrediente** integrado con Unit of Work existente
- **Middleware de autorización**: solo admin puede crear/editar/borrar ingredientes; cliente puede ver listado disponible
- **Soft delete**: ingredientes no se eliminan, se marcan como inactivos (para mantener integridad con productos)
- **Lógica de stock**: validaciones de disponibilidad, alertas de stock bajo
- **Migraciones de BD**: tabla `ingredientes` con columnas: id, nombre (unique), descripción, unidad_medida, cantidad_stock, cantidad_minima, is_active, created_at, updated_at, deleted_at

## Capabilities

### New Capabilities

- `ingrediente-management`: Creación, lectura, actualización y borrado lógico de ingredientes con validaciones y control de acceso basado en roles
- `ingrediente-stock-control`: Gestión de stock, validaciones de disponibilidad, alertas de stock bajo
- `ingrediente-search-filter`: Capacidad de listar ingredientes filtrados por estado y disponibilidad, con paginación opcional

### Modified Capabilities

- `categoria-management`: Los ingredientes podrán ser organizados por categorías (relación muchos-a-uno), extendiendo la funcionalidad existente

## Impact

- **Dependencies**: Ninguna nueva (usa stack existente: FastAPI, SQLAlchemy, Pydantic)
- **Backend folders**: Ampliación de `/routers`, `/schemas`, `/repositories`, `/services` para ingredientes
- **Database schema**: Nueva tabla `ingredientes` con índices en nombre, is_active y cantidad_stock
- **Endpoints públicos**: 5 nuevos endpoints RESTful bajo `/ingredientes`
- **Permissions**: Nuevas reglas de acceso (admin-only para POST/PUT/DELETE, public para GET listado disponible)
- **Breaking changes**: Ninguno (feature nueva)
- **Downstream**: ingrediente-crud es dependencia de producto-crud (que necesita referencias válidas a ingredientes y sus stocks)
