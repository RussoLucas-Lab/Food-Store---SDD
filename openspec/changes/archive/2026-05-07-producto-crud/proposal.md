## Why

El sistema necesita la capacidad de gestionar productos (alta, baja, modificación, consulta), que son la unidad fundamental de comercio en la plataforma. Los productos establecen el catálogo disponible para los clientes en sus pedidos, generan transacciones de venta, y crean puntos de validación críticos (precios, stock, disponibilidad). Sin ABM de productos funcional no hay catálogo navegable, pedidos creíbles, ni flujo de compra posible.

Change 5 (ingrediente-crud) entregó la gestión de ingredientes con lógica de stock. Ahora, Change 6 usa esos ingredientes como componentes constructivos para los productos, integrando también la categorización (cambio 4) y asegurando integridad: un producto debe tener al menos una categoría, puede incluir múltiples ingredientes, y debe reportar estado de stock coherente.

## What Changes

- **Alta de producto**: crear nuevo producto con nombre, descripción, categoría(s), precio base, y composición de ingredientes con cantidades.
- **Consulta de productos**: listar productos activos, filtrar por categoría, consultar disponibilidad de stock (agregado de ingredientes).
- **Modificación de productos**: cambiar precios, descripción, categorías, composición de ingredientes; actualizar estado (activo/inactivo).
- **Baja de producto**: marcar inactivo (soft delete) o eliminar si nunca fue usado en pedidos.
- **Validaciones estrictas**: precio > 0, categoría obligatoria, stock derivado de ingredientes, sin cambios de composición si hay stock insuficiente en ingredientes.
- **Integridad relacional**: producto ↔ categoría (validar existencia), producto ↔ ingrediente (validar cantidad, validar stock), bloqueo de baja si hay pedidos pendientes.

## Capabilities

### New Capabilities
- `product-crud`: Operaciones de alta, baja, modificación y consulta de productos. Incluye validación de precios, relación con categorías e ingredientes, y cálculo de disponibilidad de stock basado en ingredientes componentes.
- `product-stock-calculation`: Cálculo transparente de stock disponible para un producto como el mínimo stock disponible entre sus ingredientes, ajustado por cantidad requerida de cada ingrediente.

### Modified Capabilities
- `categoria-crud`: Ahora debe validar que una categoría no sea eliminada si hay productos activos asignados.
- `ingrediente-crud`: Ahora debe reflejar cambios de stock en los productos que lo usan como ingrediente componente.

## Impact

**Backend**:
- Nuevos modelos: `Product`, `ProductIngredient` (relación many-to-many con cantidades).
- Nuevos endpoints REST: `POST /api/products`, `GET /api/products`, `GET /api/products/:id`, `PUT /api/products/:id`, `DELETE /api/products/:id`, `GET /api/products/:id/stock`.
- Nuevas validaciones: existencia de categorías, cálculo de stock disponible, integridad relacional.
- Impacto en repo `CategoryRepository` y `IngredientRepository`: métodos nuevos para validar referencias.

**Frontend**:
- Nuevas páginas: lista de productos, detalle de producto, formulario de ABM (alta/edición).
- Nuevos componentes: selector de categorías, selector/editor de ingredientes con cantidades.
- Integraciones: comunicación con endpoints product-crud, descarga de categorías e ingredientes en formularios.

**Database**:
- Nueva tabla: `products` (id, name, description, base_price, status, created_at, updated_at).
- Nueva tabla: `product_categories` (product_id, category_id) — relación many-to-many.
- Nueva tabla: `product_ingredients` (id, product_id, ingredient_id, quantity_required) — relación many-to-many con cantidades.
