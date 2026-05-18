## 1. Modelos — Reescribir `backend/modules/pedidos/model.py`

> **Reescribir** el archivo existente. El proyecto usa clases Python puras (no SQLModel), en-memoria.
> Archivo objetivo: `backend/modules/pedidos/model.py`

- [x] 1.1 Mantener `EstadoPedidoEnum` con valores: PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO
- [x] 1.2 Clase `Pedido` con atributos: `id`, `cliente_id`, `estado` (EstadoPedidoEnum), `direccion_snapshot` (str JSON), `total` (float), `costo_envio` (float), `creado_en`, `actualizado_en`
- [x] 1.3 Clase `DetallePedido` con atributos: `id`, `pedido_id`, `producto_id`, `nombre_snapshot` (str), `cantidad` (int > 0), `precio_snapshot` (float), `personalizacion` (List[int] — IDs de ingredientes excluidos), `creado_en`
- [x] 1.4 Clase `HistorialEstadoPedido` con atributos: `id`, `pedido_id`, `estado_anterior` (Optional[EstadoPedidoEnum]), `estado_nuevo` (EstadoPedidoEnum), `usuario_id` (Optional[int]), `timestamp`, `observacion` (Optional[str])
- [x] 1.5 Cada clase tiene método `to_dict()` que retorna dict serializable
- [x] 1.6 `HistorialEstadoPedido` debe tener docstring indicando que es append-only (nunca UPDATE/DELETE)

## 2. Repositorios — Reescribir `backend/modules/pedidos/repository.py`

> **Reescribir** el archivo existente. Nombrar las clases con prefijo `InMemory` para consistencia con el resto del proyecto (ver `InMemoryCategoriaRepository`, `InMemoryProductRepository`).
> Archivo objetivo: `backend/modules/pedidos/repository.py`

- [x] 2.1 Clase `InMemoryPedidoRepository` con:
  - [x] 2.1.1 `create(pedido: Pedido) -> Pedido` — asigna ID autoincremental
  - [x] 2.1.2 `get_by_id(pedido_id: int) -> Optional[Pedido]`
  - [x] 2.1.3 `list_by_cliente(cliente_id: int, skip: int, limit: int) -> List[Pedido]` — ordenado por `creado_en` DESC
  - [x] 2.1.4 `list_all(skip: int, limit: int) -> List[Pedido]`
  - [x] 2.1.5 `update_estado(pedido_id: int, nuevo_estado: EstadoPedidoEnum) -> Optional[Pedido]` — actualiza `estado` y `actualizado_en`
  - [x] 2.1.6 `count_by_cliente(cliente_id: int) -> int`
- [x] 2.2 Clase `InMemoryDetallePedidoRepository` con:
  - [x] 2.2.1 `create(detalle: DetallePedido) -> DetallePedido`
  - [x] 2.2.2 `get_by_id(detalle_id: int) -> Optional[DetallePedido]`
  - [x] 2.2.3 `list_by_pedido(pedido_id: int) -> List[DetallePedido]`
- [x] 2.3 Clase `InMemoryHistorialEstadoPedidoRepository` con:
  - [x] 2.3.1 `create(historial: HistorialEstadoPedido) -> HistorialEstadoPedido` — único método de escritura (append-only)
  - [x] 2.3.2 `list_by_pedido(pedido_id: int) -> List[HistorialEstadoPedido]` — ordenado por `timestamp` ASC

## 3. Registrar repositorios en UoW

> Extender los dos archivos UoW del proyecto para que el PedidoService pueda acceder a los repos via `uow.pedidos`, `uow.detalles_pedido`, `uow.historial_estado`.

- [x] 3.1 En `backend/core/uow.py`: agregar tres propiedades abstractas al final de `IUnitOfWork`:
  - [x] 3.1.1 `@property @abstractmethod def pedidos(self): ...`
  - [x] 3.1.2 `@property @abstractmethod def detalles_pedido(self): ...`
  - [x] 3.1.3 `@property @abstractmethod def historial_estado(self): ...`
- [x] 3.2 En `backend/core/uow_inmemory.py`:
  - [x] 3.2.1 Importar `InMemoryPedidoRepository`, `InMemoryDetallePedidoRepository`, `InMemoryHistorialEstadoPedidoRepository` desde `backend.modules.pedidos.repository`
  - [x] 3.2.2 En `__init__`: instanciar `self._pedidos`, `self._detalles_pedido`, `self._historial_estado`
  - [x] 3.2.3 Agregar properties `pedidos`, `detalles_pedido`, `historial_estado` que retornen las instancias

## 4. Schemas — Actualizar `backend/modules/pedidos/schemas.py`

> El archivo ya existe. Verificar y completar los schemas necesarios.
> Archivo objetivo: `backend/modules/pedidos/schemas.py`

- [x] 4.1 `PersonalizacionDTO(BaseModel)` con campo `excluidos: List[int] = []`
- [x] 4.2 `CartItemDTO(BaseModel)` con: `producto_id: int`, `cantidad: int (gt=0)`, `personalizacion: PersonalizacionDTO`
- [x] 4.3 `CartCreateDTO(BaseModel)` con: `items: List[CartItemDTO] (min 1)`, `direccion_id: int`; validator que rechaza lista vacía
- [x] 4.4 `DetallePedidoResponse(BaseModel)` con: `id`, `producto_id`, `nombre_snapshot`, `cantidad`, `precio_snapshot`, `personalizacion: List[int]`, `creado_en`
- [x] 4.5 `HistorialEstadoPedidoResponse(BaseModel)` con: `id`, `estado_anterior: Optional[str]`, `estado_nuevo: str`, `usuario_id: Optional[int]`, `timestamp`, `observacion: Optional[str]`
- [x] 4.6 `PedidoResponse(BaseModel)` con: `id`, `cliente_id`, `estado: str`, `total: float`, `costo_envio: float`, `creado_en`
- [x] 4.7 `PedidoDetailResponse(BaseModel)` con: `id`, `cliente_id`, `estado: str`, `total: float`, `costo_envio: float`, `direccion_snapshot: dict`, `detalles: List[DetallePedidoResponse]`, `historial: List[HistorialEstadoPedidoResponse]`, `creado_en`, `actualizado_en`

## 5. Excepciones — Verificar `backend/modules/pedidos/exceptions.py`

> El archivo ya existe. Solo verificar que estén todas las excepciones necesarias.
> Archivo objetivo: `backend/modules/pedidos/exceptions.py`

- [x] 5.1 Verificar que existen: `CartEmptyError`, `StockInsufficient`, `PedidoNotFound`, `UnauthorizedPedidoAccess`, `DireccionNotFound`
- [x] 5.2 Todas deben tener atributo `message: str` accesible

## 6. Service Layer — Crear `backend/modules/pedidos/service.py`

> **Crear** archivo nuevo. Sigue el mismo patrón que `backend/modules/categorias/service.py`:
> - Sync (sin async/await)
> - Llama `self.uow.commit()` después de cada mutación
> - Lanza ValueError o excepciones custom que el router mapea a HTTP

- [x] 6.1 Crear clase `PedidoService` con `__init__(self, uow: IUnitOfWork)` en `backend/modules/pedidos/service.py`
- [x] 6.2 Método `create_order(self, cliente_id: int, carrito_dto: CartCreateDTO) -> dict`:
  - [x] 6.2.1 Validar que `carrito_dto.items` no está vacío → lanzar `CartEmptyError`
  - [x] 6.2.2 Para cada item: obtener producto via `self.uow.productos.get_by_id(item.producto_id)`; si no existe → lanzar `ValueError`
  - [x] 6.2.3 Validar `producto.stock >= item.cantidad` → si no → lanzar `StockInsufficient`
  - [x] 6.2.4 Obtener dirección: `self.uow.clientes.get_direccion_by_id(carrito_dto.direccion_id)` (o el método correspondiente); si no existe o no pertenece al cliente → lanzar `DireccionNotFound`
  - [x] 6.2.5 Construir `direccion_snapshot` como JSON string con campos de la dirección
  - [x] 6.2.6 Calcular `total = sum(item.cantidad * producto.precio for each item)`
  - [x] 6.2.7 Crear `Pedido` con `estado=EstadoPedidoEnum.PENDIENTE`; llamar `self.uow.pedidos.create(pedido)`
  - [x] 6.2.8 Para cada item: crear `DetallePedido` con `nombre_snapshot=producto.nombre`, `precio_snapshot=producto.precio`; llamar `self.uow.detalles_pedido.create(detalle)`
  - [x] 6.2.9 Crear `HistorialEstadoPedido` con `estado_anterior=None`, `estado_nuevo=PENDIENTE`, `usuario_id=cliente_id`; llamar `self.uow.historial_estado.create(historial)`
  - [x] 6.2.10 Llamar `self.uow.commit()`
  - [x] 6.2.11 Retornar `pedido.to_dict()`
- [x] 6.3 Método `list_orders(self, cliente_id: int, skip: int = 0, limit: int = 10) -> List[dict]`:
  - [x] 6.3.1 Llamar `self.uow.pedidos.list_by_cliente(cliente_id, skip, limit)`
  - [x] 6.3.2 Retornar `[p.to_dict() for p in pedidos]`
- [x] 6.4 Método `get_order_detail(self, pedido_id: int, cliente_id: int) -> dict`:
  - [x] 6.4.1 Llamar `self.uow.pedidos.get_by_id(pedido_id)`; si no existe → lanzar `PedidoNotFound(pedido_id)`
  - [x] 6.4.2 Si `pedido.cliente_id != cliente_id` → lanzar `UnauthorizedPedidoAccess`
  - [x] 6.4.3 Obtener detalles: `self.uow.detalles_pedido.list_by_pedido(pedido_id)`
  - [x] 6.4.4 Obtener historial: `self.uow.historial_estado.list_by_pedido(pedido_id)`
  - [x] 6.4.5 Construir y retornar dict con pedido + detalles + historial

## 7. Router — Crear `backend/modules/pedidos/router.py`

> **Crear** archivo nuevo. Sigue el patrón de `backend/modules/categorias/router.py`:
> - Instanciar UoW y Service a nivel de módulo (no por-request)
> - Usar `require_role` del middleware JWT para proteger endpoints
> - Prefijo: `/api/v1/pedidos` (el prefijo `/api/v1` va en main.py)

- [x] 7.1 Importar `InMemoryUnitOfWork`, `PedidoService`, schemas de pedidos, `require_role`
- [x] 7.2 Instanciar `uow = InMemoryUnitOfWork()` y `pedido_service = PedidoService(uow)` a nivel de módulo
- [x] 7.3 Crear `router = APIRouter(prefix="/pedidos", tags=["pedidos"])`
- [x] 7.4 Endpoint `POST /pedidos` → `create_order`:
  - [x] 7.4.1 Proteger con `Depends(require_role("client"))` (o "admin")
  - [x] 7.4.2 Recibir `CartCreateDTO` en body
  - [x] 7.4.3 Llamar `pedido_service.create_order(user_id, carrito_dto)`
  - [x] 7.4.4 Capturar `CartEmptyError` → HTTP 400
  - [x] 7.4.5 Capturar `StockInsufficient` → HTTP 400
  - [x] 7.4.6 Capturar `DireccionNotFound` → HTTP 404
  - [x] 7.4.7 Retornar `status_code=201` con `PedidoResponse`
- [x] 7.5 Endpoint `GET /pedidos` → `list_orders`:
  - [x] 7.5.1 Proteger con `Depends(require_role("client"))`
  - [x] 7.5.2 Query params: `skip: int = 0`, `limit: int = 10`
  - [x] 7.5.3 Llamar `pedido_service.list_orders(user_id, skip, limit)`
  - [x] 7.5.4 Retornar `List[PedidoResponse]`
- [x] 7.6 Endpoint `GET /pedidos/{pedido_id}` → `get_order_detail`:
  - [x] 7.6.1 Proteger con `Depends(require_role("client"))`
  - [x] 7.6.2 Path param: `pedido_id: int`
  - [x] 7.6.3 Llamar `pedido_service.get_order_detail(pedido_id, user_id)`
  - [x] 7.6.4 Capturar `PedidoNotFound` → HTTP 404
  - [x] 7.6.5 Capturar `UnauthorizedPedidoAccess` → HTTP 403
  - [x] 7.6.6 Retornar `PedidoDetailResponse`

## 8. Registrar router en `backend/main.py`

> **Modificar** el archivo existente. No crear uno nuevo.
> Archivo objetivo: `backend/main.py`

- [x] 8.1 Agregar import: `from .modules.pedidos.router import router as pedidos_router`
- [x] 8.2 Agregar: `app.include_router(pedidos_router, prefix="/api/v1")`

## 9. Tests de backend — Crear en `backend/tests/modules/pedidos/`

> Los tests van dentro del directorio feature-first de tests.
> Archivos a crear: `backend/tests/modules/pedidos/__init__.py`, `test_pedido_service.py`, `test_pedido_endpoints.py`

- [x] 9.1 Crear `backend/tests/modules/pedidos/__init__.py` (vacío)
- [x] 9.2 Crear `backend/tests/modules/pedidos/test_pedido_service.py`:
  - [x] 9.2.1 Test: `create_order` con carrito válido → retorna pedido con estado PENDIENTE
  - [x] 9.2.2 Test: `create_order` con carrito vacío → lanza `CartEmptyError`
  - [x] 9.2.3 Test: `create_order` con stock insuficiente → lanza `StockInsufficient`
  - [x] 9.2.4 Test: `create_order` con dirección inválida → lanza `DireccionNotFound`
  - [x] 9.2.5 Test: snapshots de precio y nombre no cambian si el producto se modifica después
  - [x] 9.2.6 Test: `list_orders` solo retorna pedidos del cliente correcto
  - [x] 9.2.7 Test: `get_order_detail` de pedido ajeno → lanza `UnauthorizedPedidoAccess`
  - [x] 9.2.8 Test: `get_order_detail` de pedido inexistente → lanza `PedidoNotFound`
  - [x] 9.2.9 Test: historial tiene exactamente un registro inicial (estado_anterior=None, estado_nuevo=PENDIENTE)
- [x] 9.3 Crear `backend/tests/modules/pedidos/test_pedido_endpoints.py`:
  - [x] 9.3.1 Test: `POST /api/v1/pedidos` con carrito válido → 201
  - [x] 9.3.2 Test: `POST /api/v1/pedidos` sin autenticación → 401
  - [x] 9.3.3 Test: `POST /api/v1/pedidos` con carrito vacío → 400
  - [x] 9.3.4 Test: `GET /api/v1/pedidos` solo retorna pedidos del cliente autenticado → 200
  - [x] 9.3.5 Test: `GET /api/v1/pedidos/{id}` del pedido propio → 200 con detalles e historial
  - [x] 9.3.6 Test: `GET /api/v1/pedidos/{id}` del pedido ajeno → 403
  - [x] 9.3.7 Test: `GET /api/v1/pedidos/{id}` inexistente → 404
- [x] 9.4 Ejecutar `pytest backend/tests/modules/pedidos/ -v` y verificar que todos pasan

## 10. Frontend: CartStore — Crear `frontend/src/shared/stores/cartStore.ts`

> El carrito es estado del **cliente** (localStorage persistido), no del servidor.
> Va en `shared/stores/` porque lo usan múltiples features (store, checkout, pedidos).
> Nota: Zustand no está instalado en el proyecto. Se implementó con useSyncExternalStore + localStorage.

- [x] 10.1 Crear `frontend/src/shared/stores/cartStore.ts`
- [x] 10.2 Definir interface `CartItem`: `{ producto_id: number; producto_nombre: string; precio: number; cantidad: number; personalizacion: { excluidos: number[] } }`
- [x] 10.3 Definir interface `CartStore` con estado (`items: CartItem[]`) y acciones
- [x] 10.4 Implementar store con `persist` en localStorage (key: `"food-store:cart"`)
  - [x] 10.4.1 `addItem(producto, cantidad, excluidos)` — si ya existe el producto_id, incrementar cantidad
  - [x] 10.4.2 `updateQuantity(producto_id, cantidad)` — si cantidad <= 0, quitar item
  - [x] 10.4.3 `removeItem(producto_id)`
  - [x] 10.4.4 `clearCart()`
  - [x] 10.4.5 `getTotal(): number` — suma `item.precio * item.cantidad`
  - [x] 10.4.6 `getCartDTO(): CartCreateDTO` — serializa para POST /api/v1/pedidos
- [x] 10.5 Persistir solo `items` en localStorage (no acciones)
- [x] 10.6 **Regla**: nunca `useCartStore()` sin selector. Siempre `useCartStore(s => s.items)`

## 11. Frontend: Feature pedidos — Crear `frontend/src/features/pedidos/`

> Toda la UI de carrito y checkout vive en la feature `pedidos`.
> Sigue FSD: imports permitidos de `shared/` y `features/productos/` (pero no cross entre features al mismo nivel).

- [x] 11.1 Crear `frontend/src/features/pedidos/` con subdirectorios: `components/`, `pages/`, `services/`
- [x] 11.2 Crear `frontend/src/features/pedidos/services/pedidoClient.ts`:
  - [x] 11.2.1 `createPedido(dto: CartCreateDTO): Promise<PedidoResponse>` → `POST /api/v1/pedidos`
  - [x] 11.2.2 `listPedidos(skip, limit): Promise<PedidoResponse[]>` → `GET /api/v1/pedidos`
  - [x] 11.2.3 `getPedidoDetail(id): Promise<PedidoDetailResponse>` → `GET /api/v1/pedidos/{id}`
  - [x] 11.2.4 `getMyDirecciones(): Promise<DireccionResponse[]>` → `GET /api/v1/clientes/me/direcciones`
- [x] 11.3 Crear `frontend/src/features/pedidos/components/CartItemList.tsx`:
  - [x] 11.3.1 Prop: `items` desde `useCartStore(s => s.items)`
  - [x] 11.3.2 Renderizar card por item: nombre, precio, cantidad
  - [x] 11.3.3 Botones -/+ usan `useCartStore(s => s.updateQuantity)`
  - [x] 11.3.4 Botón "Quitar" usa `useCartStore(s => s.removeItem)`
  - [x] 11.3.5 Mostrar lista de excluidos si `personalizacion.excluidos.length > 0`
- [x] 11.4 Crear `frontend/src/features/pedidos/components/CartSummary.tsx`:
  - [x] 11.4.1 Subtotal: `useCartStore(s => s.getTotal())`
  - [x] 11.4.2 Costo de envío fijo (leer de config o constante)
  - [x] 11.4.3 Total = subtotal + envío
- [x] 11.5 Crear `frontend/src/features/pedidos/components/DirectionSelector.tsx`:
  - [x] 11.5.1 Cargar direcciones con fetch directo (useQuery no disponible sin TanStack Query)
  - [x] 11.5.2 Renderizar radio buttons con direcciones disponibles
  - [x] 11.5.3 Estado local: `selectedDirectionId`; exponer via prop callback `onSelect(id)`
  - [x] 11.5.4 Link "+ Agregar Nueva Dirección" navega a la pantalla de cliente
- [x] 11.6 Crear `frontend/src/features/pedidos/components/CreateOrderButton.tsx`:
  - [x] 11.6.1 Disabled si `items.length === 0` o `selectedDirectionId === null`
  - [x] 11.6.2 Al click: llamar `createPedido(cartStore.getCartDTO())`
  - [x] 11.6.3 Loading state con spinner mientras espera respuesta
  - [x] 11.6.4 En éxito: `clearCart()`, navegar a `/pedidos/{id}`
  - [x] 11.6.5 En error: mostrar toast con mensaje del error
- [x] 11.7 Crear `frontend/src/features/pedidos/pages/CheckoutPage.tsx`:
  - [x] 11.7.1 Layout 2 columnas: izquierda `<CartItemList />`, derecha `<CartSummary />` + `<DirectionSelector />` + `<CreateOrderButton />`
  - [x] 11.7.2 Si carrito vacío: mostrar mensaje "Tu carrito está vacío" con link de vuelta al catálogo
  - [x] 11.7.3 Pasar `selectedDirectionId` y setter entre `DirectionSelector` y `CreateOrderButton`

## 12. Frontend: Routing — Actualizar `frontend/src/router.tsx`

> **Modificar** el archivo existente. No crear uno nuevo.
> Archivo objetivo: `frontend/src/router.tsx`

- [x] 12.1 Agregar ruta `/checkout` que renderiza `<CheckoutPage />` envuelta en `<ProtectedRoute />`
- [x] 12.2 Agregar ruta `/pedidos/:id` para la pantalla de confirmación (puede ser stub por ahora)
- [x] 12.3 Verificar que el router file importa desde `features/pedidos/pages/CheckoutPage`

## 13. Frontend: Tests

> Tests en `frontend/src/test/` (estructura existente del proyecto).

- [x] 13.1 Test `cartStore.test.ts`:
  - [x] 13.1.1 Test: `addItem` agrega item nuevo
  - [x] 13.1.2 Test: `addItem` mismo producto_id incrementa cantidad
  - [x] 13.1.3 Test: `updateQuantity` con 0 elimina el item
  - [x] 13.1.4 Test: `removeItem` elimina correctamente
  - [x] 13.1.5 Test: `getTotal()` retorna suma correcta
  - [x] 13.1.6 Test: `clearCart()` vacía el array
- [x] 13.2 Test `CartItemList.test.tsx`:
  - [x] 13.2.1 Test: renderiza items del store
  - [x] 13.2.2 Test: botón "+" llama `updateQuantity`
  - [x] 13.2.3 Test: botón "Quitar" llama `removeItem`
- [x] 13.3 Test `CartSummary.test.tsx`:
  - [x] 13.3.1 Test: muestra total correcto dado el estado del store
- [x] 13.4 Test `CheckoutPage.test.tsx`:
  - [x] 13.4.1 Test: muestra "carrito vacío" si no hay items
  - [x] 13.4.2 Test: renderiza `CartItemList` y `CartSummary` si hay items

## 14. Verificación final

- [x] 14.1 Ejecutar `pytest backend/ -v` — todos los tests pasan (290 passed)
- [x] 14.2 Ejecutar `npm test` en `frontend/` — todos los tests pasan (35 passed)
- [x] 14.3 Verificar estructura feature-first del backend:
  - [x] 14.3.1 `backend/modules/pedidos/model.py` ✅
  - [x] 14.3.2 `backend/modules/pedidos/repository.py` ✅
  - [x] 14.3.3 `backend/modules/pedidos/schemas.py` ✅
  - [x] 14.3.4 `backend/modules/pedidos/exceptions.py` ✅
  - [x] 14.3.5 `backend/modules/pedidos/service.py` ✅
  - [x] 14.3.6 `backend/modules/pedidos/router.py` ✅
  - [x] 14.3.7 `backend/core/uow.py` tiene abstract props pedidos/detalles_pedido/historial_estado ✅
  - [x] 14.3.8 `backend/core/uow_inmemory.py` tiene implementación de repos pedidos ✅
  - [x] 14.3.9 `backend/main.py` importa `modules.pedidos.router` ✅
  - [x] 14.3.10 **No hay archivos de pedidos** en `backend/routers/`, `backend/services/`, `backend/models/` ✅
- [x] 14.4 Verificar estructura FSD del frontend:
  - [x] 14.4.1 `frontend/src/features/pedidos/components/` tiene todos los componentes ✅
  - [x] 14.4.2 `frontend/src/features/pedidos/pages/CheckoutPage.tsx` ✅
  - [x] 14.4.3 `frontend/src/features/pedidos/services/pedidoClient.ts` ✅
  - [x] 14.4.4 `frontend/src/shared/stores/cartStore.ts` ✅
  - [x] 14.4.5 **No hay imports cruzados** entre features al mismo nivel ✅
- [ ] 14.5 `npm run lint` (frontend) sin errores
- [ ] 14.6 `npm run type-check` (frontend) sin errores
- [ ] 14.7 Test manual: crear pedido completo desde frontend
- [ ] 14.8 Sync specs finales: `openspec sync carrito-pedidos`
- [ ] 14.9 Archive: `openspec archive carrito-pedidos --yes`
