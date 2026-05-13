## 1. Database & Models Setup

- [ ] 1.1 Crear migration Alembic para tabla `pedidos`
- [ ] 1.2 Crear migration Alembic para tabla `detalles_pedido`
- [ ] 1.3 Crear migration Alembic para tabla `historial_estado_pedido` (append-only)
- [ ] 1.4 Crear modelo SQLModel `Pedido` con validaciones y constraints
- [ ] 1.5 Crear modelo SQLModel `DetallePedido` con array personalización
- [ ] 1.6 Crear modelo SQLModel `HistorialEstadoPedido`
- [ ] 1.7 Ejecutar migraciones: `alembic upgrade head`
- [ ] 1.8 Verificar tablas en PostgreSQL con \dt y columnas correcto

## 2. Backend: Repositories & Pydantic Schemas

- [ ] 2.1 Crear `PedidoRepository` (extends BaseRepository)
- [ ] 2.2 Crear `DetallePedidoRepository` (extends BaseRepository)
- [ ] 2.3 Crear `HistorialEstadoPedidoRepository` (extends BaseRepository)
- [ ] 2.4 Crear Pydantic schemas: `CartItemDTO`, `CartCreateDTO`
- [ ] 2.5 Crear Pydantic schemas: `DetallePedidoResponse`, `PedidoResponse`
- [ ] 2.6 Crear Pydantic schema: `PedidoDetailResponse`
- [ ] 2.7 Crear excepciones custom: `CartEmptyError`, `StockInsufficient`
- [ ] 2.8 Registrar repositorios en UoW

## 3. Backend: Service Layer

- [ ] 3.1 Crear `PedidoService` con método `create_order(cliente_id, carrito_dto, direccion_id)`
- [ ] 3.2 Implementar validación de stock con SELECT FOR UPDATE (transaccional)
- [ ] 3.3 Implementar generación de snapshots (precio, dirección)
- [ ] 3.4 Implementar cálculo de total (suma subtotales)
- [ ] 3.5 Implementar creación atómica: INSERT pedido + detalles + historial
- [ ] 3.6 Implementar rollback automático en errores (UoW context manager)
- [ ] 3.7 Crear método `list_orders(cliente_id, skip, limit)`
- [ ] 3.8 Crear método `get_order_detail(pedido_id, cliente_id)` con validación ownership

## 4. Backend: Endpoints

- [ ] 4.1 Crear router `pedidos.py` con prefijo `/api/v1/pedidos`
- [ ] 4.2 Implementar `POST /api/v1/pedidos` (crear pedido)
  - [ ] 4.2.1 Autenticación: get_current_user
  - [ ] 4.2.2 Validación de request (cartCreateDTO)
  - [ ] 4.2.3 Llamar PedidoService.create_order
  - [ ] 4.2.4 Return 201 Created + PedidoResponse
  - [ ] 4.2.5 Manejo de errores (400, 404, 401)
- [ ] 4.3 Implementar `GET /api/v1/pedidos` (listar pedidos del cliente)
  - [ ] 4.3.1 Autenticación: get_current_user
  - [ ] 4.3.2 Parámetros: skip, limit
  - [ ] 4.3.3 Llamar PedidoService.list_orders
  - [ ] 4.3.4 Return 200 OK + List[PedidoResponse]
- [ ] 4.4 Implementar `GET /api/v1/pedidos/{id}` (detalle de pedido)
  - [ ] 4.4.1 Autenticación: get_current_user
  - [ ] 4.4.2 Parámetro: pedido_id
  - [ ] 4.4.3 Validación de ownership (403 Forbidden si no es dueño)
  - [ ] 4.4.4 Llamar PedidoService.get_order_detail
  - [ ] 4.4.5 Return 200 OK + PedidoDetailResponse
- [ ] 4.5 Registrar router en main.py con prefijo /api/v1

## 5. Backend: Testing

- [ ] 5.1 Crear tests unitarios para PedidoService.create_order
  - [ ] 5.1.1 Test: crear pedido válido
  - [ ] 5.1.2 Test: stock insuficiente → rollback
  - [ ] 5.1.3 Test: dirección no existe → error
  - [ ] 5.1.4 Test: carrito vacío → error
  - [ ] 5.1.5 Test: snapshots son inmutables (no cambian con producto posterior)
- [ ] 5.2 Crear tests para endpoints
  - [ ] 5.2.1 Test: POST /pedidos con carrito válido
  - [ ] 5.2.2 Test: POST /pedidos sin autenticación → 401
  - [ ] 5.2.3 Test: GET /pedidos solo retorna pedidos del cliente
  - [ ] 5.2.4 Test: GET /pedidos/{id} de otro cliente → 403
- [ ] 5.3 Crear tests de transaccionalidad
  - [ ] 5.3.1 Test: transacción rollback en falla de stock
  - [ ] 5.3.2 Test: historial_estado_pedido registra transición inicial
- [ ] 5.4 Ejecutar suite de tests y validar cobertura > 80%

## 6. Frontend: CartStore Setup

- [ ] 6.1 Crear archivo `src/shared/stores/cartStore.ts`
- [ ] 6.2 Implementar interfaz `CartItem` (producto_id, cantidad, personalización)
- [ ] 6.3 Implementar interfaz `CartStore` con estado y acciones
- [ ] 6.4 Implementar Zustand store con persistencia en localStorage
  - [ ] 6.4.1 addItem(producto, cantidad, excluidos)
  - [ ] 6.4.2 updateQuantity(producto_id, cantidad)
  - [ ] 6.4.3 removeItem(producto_id)
  - [ ] 6.4.4 clearCart()
  - [ ] 6.4.5 getTotal()
  - [ ] 6.4.6 getCartDTO()
- [ ] 6.5 Implementar localStorage persistence
  - [ ] 6.5.1 saveToLocalStorage on state change
  - [ ] 6.5.2 loadFromLocalStorage on app init
- [ ] 6.6 Crear tests unitarios para cartStore
  - [ ] 6.6.1 Test: addItem
  - [ ] 6.6.2 Test: updateQuantity
  - [ ] 6.6.3 Test: removeItem
  - [ ] 6.6.4 Test: localStorage persistence
  - [ ] 6.6.5 Test: getTotal calculation

## 7. Frontend: Components

- [ ] 7.1 Crear componente `<CartItemList />`
  - [ ] 7.1.1 Prop: items from cartStore
  - [ ] 7.1.2 Render item cards con nombre, precio, cantidad
  - [ ] 7.1.3 Buttons: -/+/remove
  - [ ] 7.1.4 Mostrar personalización (excluidos)
  - [ ] 7.1.5 Update cartStore on actions
- [ ] 7.2 Crear componente `<CartSummary />`
  - [ ] 7.2.1 Mostrar subtotal (from cartStore.getTotal())
  - [ ] 7.2.2 Mostrar envío fijo ($5.00)
  - [ ] 7.2.3 Mostrar total (subtotal + envío)
  - [ ] 7.2.4 Auto-update si carrito cambia
- [ ] 7.3 Crear componente `<DirectionSelector />`
  - [ ] 7.3.1 Cargar direcciones: GET /api/v1/clientes/me/direcciones
  - [ ] 7.3.2 Render radio buttons con direcciones
  - [ ] 7.3.3 State: selectedDirectionId
  - [ ] 7.3.4 Link: "+ Agregar Nueva Dirección"
- [ ] 7.4 Crear componente `<CreateOrderButton />`
  - [ ] 7.4.1 Disabled si carrito vacío
  - [ ] 7.4.2 Disabled si no hay dirección seleccionada
  - [ ] 7.4.3 On click: POST /api/v1/pedidos
  - [ ] 7.4.4 Loading state con spinner
  - [ ] 7.4.5 Success: clearCart, navigate a /pedidos/{id}
  - [ ] 7.4.6 Error: show error toast
- [ ] 7.5 Crear componente `<OrderConfirmationModal />`
  - [ ] 7.5.1 Mostrar ID pedido, total, estado
  - [ ] 7.5.2 Buttons: "Ver Pedido", "Continuar"
  - [ ] 7.5.3 Auto-close si usuario cierra

## 8. Frontend: CheckoutPage

- [ ] 8.1 Crear página `src/pages/CheckoutPage.tsx`
- [ ] 8.2 Layout: 2 columns (carrito + summary/direccion/botón)
- [ ] 8.3 Load direcciones: useQuery GET /api/v1/clientes/me/direcciones
- [ ] 8.4 Render CartItemList (left)
- [ ] 8.5 Render CartSummary + DirectionSelector + CreateOrderButton (right)
- [ ] 8.6 Error handling: si no hay carrito, mostrar "Carrito vacío"
- [ ] 8.7 Rutas: agregar /checkout a react-router
- [ ] 8.8 Proteger ruta: requiere autenticación (ProtectedRoute)

## 9. Frontend: HTTP Client & API Integration

- [ ] 9.1 Crear método `pedidoClient.createPedido(carrito_dto)` (POST /pedidos)
- [ ] 9.2 Crear método `pedidoClient.listPedidos(skip, limit)` (GET /pedidos)
- [ ] 9.3 Crear método `pedidoClient.getPedidoDetail(id)` (GET /pedidos/{id})
- [ ] 9.4 Crear método `direccionClient.getMyDirecciones()` (GET /clientes/me/direcciones)
- [ ] 9.5 Integrar métodos en componentes (CheckoutPage, DirectionSelector, etc.)

## 10. Frontend: Testing

- [ ] 10.1 Crear tests para CartItemList
  - [ ] 10.1.1 Test: render items
  - [ ] 10.1.2 Test: +/- buttons update cartStore
  - [ ] 10.1.3 Test: remove button
- [ ] 10.2 Crear tests para CartSummary
  - [ ] 10.2.1 Test: calcular total correcto
  - [ ] 10.2.2 Test: actualizar si carrito cambia
- [ ] 10.3 Crear tests para DirectionSelector
  - [ ] 10.3.1 Test: cargar direcciones
  - [ ] 10.3.2 Test: seleccionar dirección
- [ ] 10.4 Crear tests para CreateOrderButton
  - [ ] 10.4.1 Test: disabled si carrito vacío
  - [ ] 10.4.2 Test: POST /pedidos on click
  - [ ] 10.4.3 Test: success flow
  - [ ] 10.4.4 Test: error handling
- [ ] 10.5 Crear tests para CheckoutPage
  - [ ] 10.5.1 Test: render sin errores
  - [ ] 10.5.2 Test: cargar direcciones
  - [ ] 10.5.3 Test: flujo completo checkout

## 11. Integration Testing

- [ ] 11.1 Test: Usuario agrega producto al carrito (cartStore)
- [ ] 11.2 Test: Navega a /checkout y ve carrito
- [ ] 11.3 Test: Selecciona dirección
- [ ] 11.4 Test: Click "Crear Pedido"
- [ ] 11.5 Test: Backend crea pedido con snapshots
- [ ] 11.6 Test: Frontend navega a /pedidos/{id}
- [ ] 11.7 Test: Stock insuficiente → error toast
- [ ] 11.8 Test: Transacción rollback en falla

## 12. Documentation & Cleanup

- [ ] 12.1 Documentar CartStore en `frontend/STORE_GUIDE.md`
- [ ] 12.2 Documentar endpoints en `backend/PEDIDOS_API.md`
- [ ] 12.3 Actualizar `README.md` con flujo de checkout
- [ ] 12.4 Agregar ejemplos de cURL para endpoints
- [ ] 12.5 Revisar y limpiar console logs
- [ ] 12.6 Code review: backend PedidoService
- [ ] 12.7 Code review: frontend CheckoutPage
- [ ] 12.8 Validar que no hay secrets en .env.example

## 13. Verification & Archive

- [ ] 13.1 Ejecutar suite de tests completa: `npm test && pytest`
- [ ] 13.2 Verificar cobertura backend > 80%
- [ ] 13.3 Verificar cobertura frontend > 75%
- [ ] 13.4 Linter check: `npm run lint` (frontend)
- [ ] 13.5 Type check: `npm run type-check` (frontend)
- [ ] 13.6 Build check: `npm run build` (frontend)
- [ ] 13.7 Manual testing: crear pedido completo
- [ ] 13.8 Verificar que todas las reglas de negocio se cumplen
- [ ] 13.9 Sync specs finales a openspec/specs/
- [ ] 13.10 Archive change: `openspec archive carrito-pedidos --yes`
