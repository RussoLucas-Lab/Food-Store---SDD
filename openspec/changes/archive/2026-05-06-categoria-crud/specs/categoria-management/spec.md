## ADDED Requirements

### Requirement: Crear nueva categoría
El sistema SHALL permitir a un usuario administrador crear una nueva categoría proporcionando nombre y descripción opcional. El nombre debe ser único, no vacío, y de máximo 100 caracteres. La descripción es opcional pero si se proporciona debe ser de máximo 500 caracteres. La categoría se crea con estado `is_active = true` y timestamps automáticos.

#### Scenario: Crear categoría válida
- **WHEN** un admin envía `POST /categorias` con nombre "Bebidas" y descripción "Bebidas frías y calientes"
- **THEN** la categoría se crea exitosamente, se devuelve 201 con `id`, `nombre`, `descripcion`, `is_active`, `created_at`, `updated_at`

#### Scenario: Crear categoría sin nombre
- **WHEN** un admin envía `POST /categorias` con nombre vacío
- **THEN** el sistema rechaza con 400 Bad Request indicando "nombre es requerido"

#### Scenario: Crear categoría con nombre duplicado
- **WHEN** un admin intenta crear "Bebidas" cuando ya existe una categoría con ese nombre
- **THEN** el sistema rechaza con 409 Conflict indicando "nombre ya existe"

#### Scenario: Usuario sin permiso intenta crear categoría
- **WHEN** un cliente (rol customer) envía `POST /categorias` con datos válidos
- **THEN** el sistema rechaza con 403 Forbidden indicando "Solo admins pueden crear categorías"

### Requirement: Obtener detalles de una categoría
El sistema SHALL permitir obtener los detalles completos de una categoría específica por su ID. Solo se devuelven categorías activas (`is_active = true`). Si la categoría no existe o está inactiva, se devuelve 404.

#### Scenario: Obtener categoría existente
- **WHEN** un usuario envía `GET /categorias/1`
- **THEN** el sistema devuelve 200 con los detalles de la categoría incluyendo id, nombre, descripción, is_active, created_at, updated_at

#### Scenario: Obtener categoría inexistente
- **WHEN** un usuario envía `GET /categorias/999`
- **THEN** el sistema devuelve 404 Not Found indicando "Categoría no encontrada"

#### Scenario: Obtener categoría inactiva
- **WHEN** un usuario envía `GET /categorias/5` donde categoría 5 está marcada como `is_active = false`
- **THEN** el sistema devuelve 404 indicando "Categoría no encontrada"

### Requirement: Actualizar categoría existente
El sistema SHALL permitir a un admin actualizar el nombre o descripción de una categoría existente. Se validan los mismos criterios que en creación (nombre único, longitud máxima). El timestamp `updated_at` se actualiza automáticamente.

#### Scenario: Actualizar nombre de categoría
- **WHEN** un admin envía `PUT /categorias/1` con nuevo nombre "Bebidas Frías"
- **THEN** la categoría se actualiza exitosamente, se devuelve 200 con los datos actualizados y `updated_at` reflejando la hora actual

#### Scenario: Intentar actualizar a nombre duplicado
- **WHEN** un admin intenta cambiar nombre de categoría A a un nombre que ya usa categoría B
- **THEN** el sistema rechaza con 409 Conflict indicando "nombre ya existe"

#### Scenario: Usuario sin permiso intenta actualizar
- **WHEN** un cliente envía `PUT /categorias/1` con datos válidos
- **THEN** el sistema rechaza con 403 Forbidden indicando "Solo admins pueden actualizar categorías"

#### Scenario: Actualizar categoría inexistente
- **WHEN** un admin envía `PUT /categorias/999` con datos válidos
- **THEN** el sistema devuelve 404 Not Found indicando "Categoría no encontrada"

### Requirement: Eliminar (marcar como inactiva) una categoría
El sistema SHALL permitir a un admin marcar una categoría como inactiva (soft delete). La categoría no se elimina de la BD, pero deja de aparecer en listados públicos. Si la categoría ya está inactiva, la operación es idempotente (devuelve 200 sin cambios).

#### Scenario: Marcar categoría como inactiva
- **WHEN** un admin envía `DELETE /categorias/1` donde la categoría está activa
- **THEN** la categoría se marca como `is_active = false`, `deleted_at` se setea a la hora actual, se devuelve 204 No Content

#### Scenario: Usuario sin permiso intenta eliminar
- **WHEN** un cliente envía `DELETE /categorias/1`
- **THEN** el sistema rechaza con 403 Forbidden indicando "Solo admins pueden eliminar categorías"

#### Scenario: Eliminar categoría inexistente
- **WHEN** un admin envía `DELETE /categorias/999`
- **THEN** el sistema devuelve 404 Not Found indicando "Categoría no encontrada"

#### Scenario: Eliminar categoría ya inactiva (idempotencia)
- **WHEN** un admin envía `DELETE /categorias/1` donde la categoría ya está `is_active = false`
- **THEN** el sistema devuelve 204 No Content sin hacer cambios

### Requirement: Listar todas las categorías
El sistema SHALL permitir a cualquier usuario (autenticado o no, según políticas futuras) listar todas las categorías activas. Solo se devuelven categorías con `is_active = true`. Se devuelve un array vacío si no hay categorías activas.

#### Scenario: Listar categorías cuando existen
- **WHEN** un usuario envía `GET /categorias`
- **THEN** el sistema devuelve 200 con un array de categorías activas, cada una con id, nombre, descripción, is_active, created_at, updated_at

#### Scenario: Listar categorías cuando no existen
- **WHEN** un usuario envía `GET /categorias` y no hay categorías activas en la BD
- **THEN** el sistema devuelve 200 con un array vacío `[]`

### Requirement: Validar formato de entrada
El sistema SHALL validar todos los inputs en schemas Pydantic antes de procesar. Se rechaza cualquier input que no cumpla formato o constraints. Los mensajes de error deben ser específicos.

#### Scenario: Nombre con caracteres inválidos
- **WHEN** un admin envía nombre con caracteres especiales peligrosos (ej: `<script>` o SQL injection)
- **THEN** el sistema rechaza con 422 Unprocessable Entity indicando qué campo y por qué

#### Scenario: Descripción exceede longitud máxima
- **WHEN** un admin envía descripción de 501 caracteres (máx 500)
- **THEN** el sistema rechaza con 422 indicando "descripción debe tener máximo 500 caracteres"
