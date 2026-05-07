## Why

Food Store necesita un sistema de gestión de categorías de productos para organizar el catálogo y permitir que administradores clasifiquen productos. Las categorías son la base para la búsqueda, filtrado y navegación del cliente, y son requisito previo para el CRUD de productos. Sin categorías, no hay forma de estructurar el inventario.

## What Changes

- **Nuevo modelo Categoría** con nombre, descripción, estado activo/inactivo, timestamps
- **Endpoints CRUD**: `POST /categorias` (crear), `GET /categorias` (listar), `GET /categorias/{id}` (detalle), `PUT /categorias/{id}` (actualizar), `DELETE /categorias/{id}` (marcar como inactiva)
- **Validaciones**: nombre único, no vacío, longitud máxima; descripción opcional pero sanitizada
- **Repository de Categoría** integrado con Unit of Work existente
- **Middleware de autorización**: solo admin puede crear/editar/borrar categorías; cliente puede ver listado
- **Soft delete**: categorías no se eliminan, se marcan como inactivas (para mantener integridad con productos)
- **Migraciones de BD**: tabla `categorias` con columnas: id, nombre (unique), descripción, is_active, created_at, updated_at, deleted_at

## Capabilities

### New Capabilities

- `categoria-management`: Creación, lectura, actualización y borrado lógico de categorías con validaciones y control de acceso basado en roles
- `categoria-search-filter`: Capacidad de listar categorías filtradas por estado, con paginación opcional

### Modified Capabilities

- (none)

## Impact

- **Dependencies**: Ninguna nueva (usa stack existente: FastAPI, SQLAlchemy, Pydantic)
- **Backend folders**: Ampliación de `/routers`, `/schemas`, `/repositories`, `/services` para categorías
- **Database schema**: Nueva tabla `categorias` con índices en nombre y is_active
- **Endpoints públicos**: 5 nuevos endpoints RESTful bajo `/categorias`
- **Permissions**: Nuevas reglas de acceso (admin-only para POST/PUT/DELETE, public para GET)
- **Breaking changes**: Ninguno (feature nueva)
- **Downstream**: categoria-crud es dependencia de ingrediente-crud y producto-crud (ambos necesitan referencias válidas a categorías)
