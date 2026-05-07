## ADDED Requirements

### Requirement: Crear nuevo ingrediente
El sistema SHALL permitir a un usuario administrador crear un nuevo ingrediente proporcionando nombre, descripción opcional, unidad de medida, cantidad inicial de stock, y cantidad mínima. El nombre debe ser único, no vacío, y de máximo 100 caracteres. La unidad de medida debe ser una de: gramos, litros, unidades, kilos, mililitros. La cantidad de stock no puede ser negativa. La descripción es opcional pero si se proporciona debe ser de máximo 500 caracteres. El ingrediente se crea con estado `is_active = true` y timestamps automáticos.

#### Scenario: Crear ingrediente válido
- **WHEN** un admin envía `POST /ingredientes` con nombre "Sal", unidad "gramos", stock inicial 1000, cantidad mínima 100
- **THEN** el ingrediente se crea exitosamente, se devuelve 201 con `id`, `nombre`, `unidad_medida`, `cantidad_stock`, `cantidad_minima`, `is_active`, `created_at`, `updated_at`

#### Scenario: Crear ingrediente sin nombre
- **WHEN** un admin envía `POST /ingredientes` con nombre vacío
- **THEN** el sistema rechaza con 400 Bad Request indicando "nombre es requerido"

#### Scenario: Crear ingrediente con nombre duplicado
- **WHEN** un admin intenta crear "Harina" cuando ya existe un ingrediente con ese nombre
- **THEN** el sistema rechaza con 409 Conflict indicando "nombre ya existe"

#### Scenario: Usuario sin permiso intenta crear ingrediente
- **WHEN** un cliente (rol customer) envía `POST /ingredientes` con datos válidos
- **THEN** el sistema rechaza con 403 Forbidden indicando "Solo admins pueden crear ingredientes"

#### Scenario: Crear ingrediente con unidad de medida inválida
- **WHEN** un admin envía `POST /ingredientes` con unidad_medida "toneladas" (no válida)
- **THEN** el sistema rechaza con 422 Unprocessable Entity indicando "unidad_medida debe ser uno de: gramos, litros, unidades, kilos, mililitros"

#### Scenario: Crear ingrediente con stock negativo
- **WHEN** un admin envía `POST /ingredientes` con cantidad_stock -50
- **THEN** el sistema rechaza con 422 indicando "cantidad_stock no puede ser negativa"

### Requirement: Obtener detalles de un ingrediente
El sistema SHALL permitir obtener los detalles completos de un ingrediente específico por su ID. Solo se devuelven ingredientes activos (`is_active = true`). Si el ingrediente no existe o está inactivo, se devuelve 404.

#### Scenario: Obtener ingrediente existente
- **WHEN** un usuario envía `GET /ingredientes/1`
- **THEN** el sistema devuelve 200 con los detalles del ingrediente incluyendo id, nombre, unidad_medida, cantidad_stock, cantidad_minima, is_active, created_at, updated_at

#### Scenario: Obtener ingrediente inexistente
- **WHEN** un usuario envía `GET /ingredientes/999`
- **THEN** el sistema devuelve 404 Not Found indicando "Ingrediente no encontrado"

#### Scenario: Obtener ingrediente inactivo
- **WHEN** un usuario envía `GET /ingredientes/5` donde el ingrediente está marcado como `is_active = false`
- **THEN** el sistema devuelve 404 indicando "Ingrediente no encontrado"

### Requirement: Actualizar ingrediente existente
El sistema SHALL permitir a un admin actualizar el nombre, descripción, cantidad de stock o cantidad mínima de un ingrediente existente. Se validan los mismos criterios que en creación. El timestamp `updated_at` se actualiza automáticamente.

#### Scenario: Actualizar stock de ingrediente
- **WHEN** un admin envía `PUT /ingredientes/1` con cantidad_stock 2000
- **THEN** el ingrediente se actualiza exitosamente, se devuelve 200 con los datos actualizados y `updated_at` reflejando la hora actual

#### Scenario: Intentar actualizar a nombre duplicado
- **WHEN** un admin intenta cambiar nombre de ingrediente A a un nombre que ya usa ingrediente B
- **THEN** el sistema rechaza con 409 Conflict indicando "nombre ya existe"

#### Scenario: Usuario sin permiso intenta actualizar
- **WHEN** un cliente envía `PUT /ingredientes/1` con datos válidos
- **THEN** el sistema rechaza con 403 Forbidden indicando "Solo admins pueden actualizar ingredientes"

#### Scenario: Actualizar ingrediente inexistente
- **WHEN** un admin envía `PUT /ingredientes/999` con datos válidos
- **THEN** el sistema devuelve 404 Not Found indicando "Ingrediente no encontrado"

#### Scenario: Actualizar cantidad mínima a valor mayor que stock actual
- **WHEN** un admin envía `PUT /ingredientes/1` con cantidad_minima 5000 donde stock actual es 2000
- **THEN** el sistema permite la actualización (cantidad_minima es solo alerta), devuelve 200 con los datos actualizados

### Requirement: Eliminar (marcar como inactivo) un ingrediente
El sistema SHALL permitir a un admin marcar un ingrediente como inactivo (soft delete). El ingrediente no se elimina de la BD, pero deja de aparecer en listados públicos. Si el ingrediente ya está inactivo, la operación es idempotente (devuelve 204 sin cambios).

#### Scenario: Marcar ingrediente como inactivo
- **WHEN** un admin envía `DELETE /ingredientes/1` donde el ingrediente está activo
- **THEN** el ingrediente se marca como `is_active = false`, `deleted_at` se setea a la hora actual, se devuelve 204 No Content

#### Scenario: Usuario sin permiso intenta eliminar
- **WHEN** un cliente envía `DELETE /ingredientes/1`
- **THEN** el sistema rechaza con 403 Forbidden indicando "Solo admins pueden eliminar ingredientes"

#### Scenario: Eliminar ingrediente inexistente
- **WHEN** un admin envía `DELETE /ingredientes/999`
- **THEN** el sistema devuelve 404 Not Found indicando "Ingrediente no encontrado"

#### Scenario: Eliminar ingrediente ya inactivo (idempotencia)
- **WHEN** un admin envía `DELETE /ingredientes/1` donde el ingrediente ya está `is_active = false`
- **THEN** el sistema devuelve 204 No Content sin hacer cambios

### Requirement: Validar formato de entrada
El sistema SHALL validar todos los inputs en schemas Pydantic antes de procesar. Se rechaza cualquier input que no cumpla formato o constraints. Los mensajes de error deben ser específicos.

#### Scenario: Nombre con caracteres inválidos
- **WHEN** un admin envía nombre con caracteres especiales peligrosos (ej: `<script>` o SQL injection)
- **THEN** el sistema rechaza con 422 Unprocessable Entity indicando qué campo y por qué

#### Scenario: Descripción excede longitud máxima
- **WHEN** un admin envía descripción de 501 caracteres (máx 500)
- **THEN** el sistema rechaza con 422 indicando "descripción debe tener máximo 500 caracteres"
