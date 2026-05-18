## Why

Food Store necesita permitir a los clientes seleccionar productos, personalizarlos (excluir ingredientes), y crear pedidos. El carrito es el mecanismo central de compra: client-side con Zustand + localStorage para persistencia. La creación de pedidos genera snapshots de precios y direcciones, valida stock con transacciones atómicas (Unit of Work), y nace en estado PENDIENTE. Sin carrito-pedidos no hay flujo de compra, y sin pedidos no hay pago ni despacho. Esto es el corazón del e-commerce.

## What Changes

### Backend (FastAPI)

- **Modelos Pedido**: Tabla `pedidos` con cliente_id, dirección_snapshot, total, estado_id, timestamps.
- **Modelos DetallePedido**: Tabla `detalles_pedido` con cantidad, precio_snapshot, personalización (array de IDs de ingredientes).
- **Modelos HistorialEstadoPedido**: Tabla append-only para auditoría de transiciones de estado.
- **Endpoints POST /api/v1/pedidos**: Crear pedido (validar carrito, stock, generar snapshots, transacción atómica con UoW).
- **Endpoints GET /api/v1/pedidos**: Listar pedidos del cliente autenticado.
- **Endpoints GET /api/v1/pedidos/{id}**: Obtener detalle de un pedido específico.
- **PedidoService**: Lógica de creación atómica, validación de stock, snapshot generación.
- **PedidoRepository** + **DetallePedidoRepository**: Persistencia de pedidos y detalles.
- **Transacciones atómicas**: Usar UoW para garantizar "todo o nada" en creación de pedidos.

### Frontend (React)

- **CartStore (Zustand)**: Estado global del carrito con localStorage.
  - Items: `{producto_id, cantidad, personalización: [ingredientes_excluidos]}`.
  - Acciones: addItem, removeItem, updateQuantity, clearCart, getTotal.
  - Persistencia: saveToLocalStorage, loadFromLocalStorage.
- **CheckoutPage**: Página donde el usuario revisa carrito, selecciona dirección, y crea pedido.
- **Componentes**: CartSummary, CartItemList, DirectionSelector, OrderConfirmationModal.
- **HTTP**: Endpoint POST /api/v1/pedidos llamado desde frontend con carrito serializado.
- **Estado**: Después de crear pedido, redirigir a detallepedido/{id} o confirmación.

## Capabilities

### New Capabilities

- `carrito-manejo`: Agregar/editar/quitar productos al carrito con persistencia en localStorage.
- `carrito-personalizacion`: Excluir ingredientes específicos de productos en el carrito.
- `carrito-total`: Calcular total del carrito (suma de subtotales de items).
- `pedido-creacion`: Crear pedido atómico desde carrito, generar snapshots de precio y dirección.
- `pedido-validacion-stock`: Validar stock suficiente de todos los productos antes de crear pedido.
- `pedido-listado`: Listar todos los pedidos del cliente autenticado (con paginación).
- `pedido-detalle`: Obtener detalles completos de un pedido (incluyendo historial de estados).

### Modified Capabilities

- `cliente-crud`: El cliente ahora puede crear pedidos asociados a su cuenta (relación 1:N).
- `producto-crud`: Los productos se consultan para validar stock y generar snapshots al crear pedidos.

## Impact

### Backend
- Nuevos modelos SQLModel: Pedido, DetallePedido, HistorialEstadoPedido.
- Nuevas tablas PostgreSQL con migraciones Alembic.
- Nuevos endpoints REST: POST /pedidos (crear), GET /pedidos (listar), GET /pedidos/{id} (detalle).
- PedidoService y PedidoRepository con lógica de validación y snapshots.
- UoW mejorado para manejar transacciones complejas de pedidos.

### Frontend
- New Store: CartStore (Zustand) con persistencia en localStorage.
- New Page: CheckoutPage (carrito + selector de dirección + botón crear pedido).
- New Components: CartItemList, CartSummary, DirectionSelector, OrderConfirmationModal.
- HTTP client mejorado para llamar al endpoint POST /pedidos.

### Database
- Nueva tabla `pedidos` con FK a cliente_id, estado_id, direccion_entrega.
- Nueva tabla `detalles_pedido` con FK a pedido_id, producto_id, y array personalización.
- Nueva tabla `historial_estado_pedido` para auditoría (append-only).
- Índices en pedidos.cliente_id, pedidos.estado_id, detalles_pedido.pedido_id.

### Auth
- Endpoints de pedidos requieren autenticación (JWT válido).
- Un CLIENT solo puede ver/crear sus propios pedidos (validación por cliente_id == usuario.id).
- ADMIN y GESTOR_PEDIDOS pueden ver todos los pedidos (regla de negocio futura).

### Dependencias
- Nada nuevo: usa stack existente (FastAPI, SQLModel, Zustand, Axios).
- Depende de: producto-crud ✅, cliente-crud ✅, auth-roles ✅.

## Risk & Gotchas

- **Stock concurrency**: Múltiples clientes comprando simultáneamente. Mitigado con SELECT FOR UPDATE en transacción.
- **Carrito stale**: Usuario cierra navegador, productos cambian precios/stock, reabre. Mitigado con validación en creación.
- **Snapshots immutables**: Cambios futuros en productos no deben afectar pedidos. Almacenar precio/dirección en el momento.
- **Personalización array**: PostgreSQL INTEGER[] debe soportarse en SQLModel (usar JSON field si es necesario).
