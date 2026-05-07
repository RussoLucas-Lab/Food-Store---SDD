## MODIFIED Requirements

### Requirement: Eliminar categoría
La capacidad de eliminar categorías ahora SHALL validar que no exista ningún producto activo asignado a esa categoría antes de permitir la eliminación.

#### Scenario: Intento de eliminar categoría sin productos
- **WHEN** DELETE /api/categories/:id en categoría sin productos activos asignados
- **THEN** se elimina la categoría, se retorna 204 No Content

#### Scenario: Intento de eliminar categoría con productos
- **WHEN** DELETE /api/categories/:id en categoría con al menos un producto activo
- **THEN** se retorna 409 Conflict con mensaje "cannot delete category in use by products"

#### Scenario: Desactivar categoría (alternativa a eliminación)
- **WHEN** PUT /api/categories/:id con { status: "inactive" }
- **THEN** se marca la categoría inactiva pero sus productos permanecen intactos (opcionalmente implementar)
