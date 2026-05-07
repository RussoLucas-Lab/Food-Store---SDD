## MODIFIED Requirements

### Requirement: Eliminar ingrediente
La capacidad de eliminar ingredientes ahora SHALL validar que no exista ningún producto activo que lo use como componente antes de permitir la eliminación.

#### Scenario: Intento de eliminar ingrediente sin productos
- **WHEN** DELETE /api/ingredients/:id en ingrediente sin productos activos que lo usen
- **THEN** se elimina el ingrediente, se retorna 204 No Content

#### Scenario: Intento de eliminar ingrediente con productos
- **WHEN** DELETE /api/ingredients/:id en ingrediente usado en al menos un producto activo
- **THEN** se retorna 409 Conflict con mensaje "cannot delete ingredient in use by products"

#### Scenario: Actualización de stock en ingrediente se refleja en productos
- **WHEN** PUT /api/ingredients/:id con { stock_disponible: nuevo_valor }
- **THEN** GET /api/products/P/stock (para cualquier producto P que use este ingrediente) retorna el nuevo cálculo de stock automáticamente
