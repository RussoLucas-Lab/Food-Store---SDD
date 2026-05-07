## ADDED Requirements

### Requirement: Crear nuevo producto con composición de ingredientes
El sistema backend SHALL permitir la creación de un nuevo producto especificando nombre, descripción, precio base, categoría(s) obligatoria(s), e ingredientes con cantidades requeridas.

#### Scenario: Alta exitosa de producto
- **WHEN** POST /api/products con body { name, description, base_price, categories: [id1, id2], ingredients: [{ingredient_id, quantity_required}] } válido
- **THEN** se crea el producto, se retorna 201 Created con Location header y payload del producto creado

#### Scenario: Validación de campos requeridos
- **WHEN** POST /api/products sin name, sin base_price, o sin categories
- **THEN** se retorna 400 Bad Request con mensaje de validación

#### Scenario: Validación de precio
- **WHEN** POST /api/products con base_price <= 0 o no numérico
- **THEN** se retorna 400 Bad Request indicando "price must be > 0"

#### Scenario: Validación de categorías
- **WHEN** POST /api/products con categories array vacío o con category_id inexistente
- **THEN** se retorna 400 Bad Request indicando "invalid categories"

#### Scenario: Validación de ingredientes
- **WHEN** POST /api/products con ingredients array vacío o con ingredient_id inexistente o quantity_required <= 0
- **THEN** se retorna 400 Bad Request indicando "invalid ingredients"

#### Scenario: Uniqueness de nombre
- **WHEN** POST /api/products con name que ya existe en BD
- **THEN** se retorna 409 Conflict indicando "product name already exists"

### Requirement: Consultar producto por ID
El sistema backend SHALL retornar los detalles de un producto existente, incluyendo su composición de ingredientes y categorías asignadas.

#### Scenario: Consulta exitosa
- **WHEN** GET /api/products/:id con id válido
- **THEN** se retorna 200 OK con payload { id, name, description, base_price, status, categories: [...], ingredients: [{id, ingredient_id, name, quantity_required, stock_disponible_ingrediente}], created_at, updated_at }

#### Scenario: Producto no existe
- **WHEN** GET /api/products/:id con id inexistente
- **THEN** se retorna 404 Not Found

### Requirement: Listar productos con filtros
El sistema backend SHALL retornar listado de productos activos, con posibilidad de filtrar por categoría y nombre.

#### Scenario: Listar todos los productos activos
- **WHEN** GET /api/products sin parámetros
- **THEN** se retorna 200 OK con array de productos (status = active), paginado si es necesario

#### Scenario: Filtrar por categoría
- **WHEN** GET /api/products?category=categoria-id
- **THEN** se retorna 200 OK solo con productos que contengan esa categoría

#### Scenario: Filtrar por nombre (substring)
- **WHEN** GET /api/products?search=pizz
- **THEN** se retorna 200 OK con productos cuyo nombre contenga "pizz" (case-insensitive)

#### Scenario: Incluir productos inactivos
- **WHEN** GET /api/products?status=all o ?status=inactive
- **THEN** se retorna 200 OK con productos inactivos también (solo si usuario tiene permisos de administrador)

### Requirement: Calcular stock disponible de producto
El sistema backend SHALL calcular la disponibilidad de stock de un producto como el mínimo stock disponible de sus ingredientes, ajustado por cantidad requerida.

#### Scenario: Cálculo correcto de stock
- **WHEN** Producto P tiene ingrediente I1 (cantidad 2 unidades) con stock 10, e ingrediente I2 (cantidad 3) con stock 6
- **THEN** GET /api/products/P/stock retorna { stock_disponible: min(10/2, 6/3) = min(5, 2) = 2 unidades del producto }

#### Scenario: Stock cero si algún ingrediente tiene stock insuficiente
- **WHEN** Producto P tiene ingrediente I1 (cantidad 2) con stock 10, e ingrediente I2 (cantidad 1) con stock 0
- **THEN** GET /api/products/P/stock retorna { stock_disponible: 0 }

#### Scenario: Actualización transitiva al cambiar ingrediente stock
- **WHEN** Ingrediente I1 usado en Producto P tiene stock actualizado
- **THEN** GET /api/products/P/stock retorna el nuevo cálculo automáticamente sin cambiar P

### Requirement: Actualizar producto (edición)
El sistema backend SHALL permitir editar nombre, descripción, precio, categorías e ingredientes de un producto activo.

#### Scenario: Edición exitosa
- **WHEN** PUT /api/products/:id con cambios válidos
- **THEN** se actualiza el producto, se retorna 200 OK con payload actualizado

#### Scenario: No permitir edición de producto usado en pedidos
- **WHEN** PUT /api/products/:id si el producto ya está en un pedido (paid o entregado)
- **THEN** se retorna 403 Forbidden indicando "cannot modify product with active orders"

#### Scenario: Validación de cambios
- **WHEN** PUT /api/products/:id con base_price <= 0 o categories vacío
- **THEN** se retorna 400 Bad Request

#### Scenario: Cambio de composición de ingredientes
- **WHEN** PUT /api/products/:id cambiando ingredientes o cantidades
- **THEN** se actualiza la composición si todos los ingredientes tienen suficiente stock disponible; si no, retorna 400 Bad Request indicando "insufficient stock in ingredients"

### Requirement: Desactivar / eliminar producto
El sistema backend SHALL permitir cambiar el estado de un producto a inactivo (soft delete) o eliminarlo definitivamente si nunca fue usado.

#### Scenario: Soft delete (desactivar)
- **WHEN** DELETE /api/products/:id en producto usado en pedidos históricos
- **THEN** se cambia status a "inactive", se retorna 204 No Content, el producto ya no aparece en listados públicos

#### Scenario: Hard delete (eliminar)
- **WHEN** DELETE /api/products/:id en producto nunca usado en pedidos
- **THEN** se elimina la fila de BD completamente, se retorna 204 No Content

#### Scenario: Reactivar producto inactivo
- **WHEN** PUT /api/products/:id con body { status: "active" }
- **THEN** se reactiva el producto (opcionalmente, si no es parte de requerimientos actuales, omitir)

### Requirement: Validación de integridad al eliminar categoría o ingrediente
El sistema backend SHALL prevenir la eliminación de categorías o ingredientes si hay productos activos que los usan.

#### Scenario: Intento de eliminar categoría en uso
- **WHEN** DELETE /api/categories/:id si existe al menos un producto activo asignado a esa categoría
- **THEN** se retorna 409 Conflict indicando "category in use by products"

#### Scenario: Intento de eliminar ingrediente en uso
- **WHEN** DELETE /api/ingredients/:id si existe al menos un producto activo que usa ese ingrediente
- **THEN** se retorna 409 Conflict indicando "ingredient in use by products"

### Requirement: Relación many-to-many: Producto ↔ Categoría
El sistema backend SHALL mantener una relación muchos-a-muchos entre Productos y Categorías, permitiendo que un producto esté en múltiples categorías.

#### Scenario: Producto en múltiples categorías
- **WHEN** se crea Producto P con categories: [cat1_id, cat2_id]
- **THEN** GET /api/products/P retorna categories: [{id: cat1_id, ...}, {id: cat2_id, ...}]

#### Scenario: Filtrar productos por categoría retorna todas las coincidencias
- **WHEN** GET /api/products?category=cat1_id
- **THEN** retorna todos los productos que tengan cat1 asignada, aunque tengan otras categorías también

### Requirement: Relación many-to-many con cantidades: Producto ↔ Ingrediente
El sistema backend SHALL mantener una relación muchos-a-muchos entre Productos e Ingredientes con cantidad requerida por cada relación.

#### Scenario: Producto con múltiples ingredientes en cantidades específicas
- **WHEN** se crea Producto P con ingredients: [{ingredient_id: ing1, quantity_required: 2}, {ingredient_id: ing2, quantity_required: 3}]
- **THEN** GET /api/products/P retorna ingredients: [{id: ing1, quantity_required: 2, ...}, {id: ing2, quantity_required: 3, ...}]

#### Scenario: Cambiar cantidad de ingrediente
- **WHEN** PUT /api/products/:id con ingredients[0].quantity_required = 5 (antes era 2)
- **THEN** se actualiza la cantidad, el stock calculado se recalcula con el nuevo valor

#### Scenario: Remover ingrediente de composición
- **WHEN** PUT /api/products/:id con ingredients array que no incluye un ingredient_id anterior
- **THEN** se remueve esa relación ProductIngredient de la BD
