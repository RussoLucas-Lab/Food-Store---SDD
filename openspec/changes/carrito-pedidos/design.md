## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CheckoutPage                                                    │
│  ├─ CartItemList (read cartStore)                                │
│  ├─ CartSummary (cartStore total)                                │
│  ├─ DirectionSelector (list direcciones, select una)             │
│  └─ CreateOrderButton (POST /api/v1/pedidos)                     │
│                                                                   │
│  CartStore (Zustand + localStorage)                              │
│  ├─ items: [{producto_id, cantidad, personalización}]            │
│  ├─ addItem(producto, cantidad, personalización)                 │
│  ├─ removeItem(producto_id)                                      │
│  ├─ updateQuantity(producto_id, cantidad)                        │
│  ├─ clearCart()                                                  │
│  ├─ getTotal()  (computed)                                       │
│  └─ getCartDTO()  (serializar para POST)                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            HTTP Client
                   POST /api/v1/pedidos { carrito }
                   GET /api/v1/pedidos
                   GET /api/v1/pedidos/{id}
└─────────────────────────────────────────────────────────────────┘
│                      BACKEND (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  POST /api/v1/pedidos: CreateOrderEndpoint                        │
│  ├─ get_current_user (JWT auth)                                  │
│  ├─ PedidoService.create_order(cliente_id, carrito_dto)          │
│  │  ├─ UoW begin transaction                                     │
│  │  ├─ Validate stock (SELECT FOR UPDATE)                        │
│  │  ├─ Generar snapshots (precio, dirección)                     │
│  │  ├─ Create Pedido (estado=PENDIENTE)                          │
│  │  ├─ Create DetallePedido items                                │
│  │  ├─ Create HistorialEstadoPedido (PENDIENTE)                  │
│  │  └─ UoW commit (rollback on error)                            │
│  └─ Return: {id, total, estado, detalles}                        │
│                                                                   │
│  GET /api/v1/pedidos: ListOrdersEndpoint                          │
│  ├─ get_current_user                                             │
│  ├─ PedidoService.list_orders(cliente_id, skip, limit)           │
│  └─ Return: [{id, total, estado, creado_en}, ...]               │
│                                                                   │
│  GET /api/v1/pedidos/{id}: GetOrderEndpoint                       │
│  ├─ get_current_user                                             │
│  ├─ Validate ownership (pedido.cliente_id == user.id)            │
│  ├─ PedidoService.get_order_detail(pedido_id)                    │
│  └─ Return: {id, cliente, detalles, historial, total}            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
│                      DATABASE (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  pedidos                                                          │
│  ├─ id (PK)                                                       │
│  ├─ cliente_id (FK → usuarios)                                   │
│  ├─ estado_id (FK → estado_pedido)  [default = 1 PENDIENTE]      │
│  ├─ direccion_snapshot (JSON/TEXT) [inmutable snapshot]          │
│  ├─ total (NUMERIC)                                              │
│  ├─ creado_en (timestamp, default NOW)                           │
│  ├─ actualizado_en (timestamp, auto-update)                      │
│  └─ Índices: (cliente_id), (estado_id)                           │
│                                                                   │
│  detalles_pedido                                                  │
│  ├─ id (PK)                                                       │
│  ├─ pedido_id (FK → pedidos)                                     │
│  ├─ producto_id (FK → productos)                                 │
│  ├─ cantidad (int > 0)                                           │
│  ├─ precio_snapshot (NUMERIC) [inmutable]                        │
│  ├─ personalizacion (INTEGER[] | JSON) [excluidos ingredientes]  │
│  ├─ creado_en (timestamp, default NOW)                           │
│  └─ Índices: (pedido_id)                                         │
│                                                                   │
│  historial_estado_pedido (append-only, nunca UPDATE/DELETE)      │
│  ├─ id (PK)                                                       │
│  ├─ pedido_id (FK → pedidos)                                     │
│  ├─ estado_anterior_id (FK → estado_pedido)                      │
│  ├─ estado_nuevo_id (FK → estado_pedido)                         │
│  ├─ usuario_id (FK → usuarios, nullable si es SISTEMA)           │
│  ├─ timestamp (timestamp, default NOW)                           │
│  ├─ observacion (TEXT nullable)                                  │
│  └─ Índices: (pedido_id)                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend: CartStore (Zustand)

```typescript
interface CartItem {
  producto_id: string;
  producto_nombre: string;
  precio: number;
  cantidad: number;
  personalizacion: {
    excluidos: number[]; // array de ingrediente_ids excluidos
  };
}

interface CartStore {
  items: CartItem[];
  
  // Mutations
  addItem(producto: Producto, cantidad: number, excluidos?: number[]): void;
  removeItem(producto_id: string): void;
  updateQuantity(producto_id: string, cantidad: number): void;
  clearCart(): void;
  
  // Getters
  getTotal(): number;
  getCartDTO(): CartCreateDTO;
}

// localStorage key: "food-store:cart"
// persisted: items array
```

### Frontend: CheckoutPage

```
CheckoutPage
├─ Load directions (GET /api/v1/clientes/me/direcciones)
├─ Display CartItemList (from cartStore)
├─ Display CartSummary (total + shipping estimate)
├─ DirectionSelector (radio buttons, select default or pick another)
├─ Buttons:
│  ├─ Continue Shopping (nav back)
│  └─ Create Order (POST /api/v1/pedidos)
├─ On Success:
│  ├─ clearCart()
│  ├─ redirect to /pedidos/{id}
│  └─ show OrderConfirmationModal
└─ On Error: show error toast
```

### Backend: PedidoService

```python
class PedidoService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def create_order(
        self, 
        cliente_id: str, 
        carrito_dto: CartCreateDTO,
        direccion_id: str
    ) -> PedidoResponse:
        """
        Crea un pedido de forma ATÓMICA:
        1. Validar stock suficiente (SELECT FOR UPDATE)
        2. Generar snapshots de precios
        3. Generar snapshot de dirección
        4. Crear Pedido (estado=PENDIENTE)
        5. Crear DetallePedido items
        6. Crear HistorialEstadoPedido
        Si algo falla, rollback automático del UoW.
        """
        async with self.uow:
            # 1. Validar stock y generar snapshots
            detalles_snapshot = []
            for item in carrito_dto.items:
                producto = await self.uow.productos.get_by_id(item.producto_id)
                if not producto:
                    raise ProductoNotFound()
                if producto.stock < item.cantidad:
                    raise StockInsufficient(
                        f"Stock insuficiente para {producto.nombre}"
                    )
                detalles_snapshot.append({
                    "producto_id": item.producto_id,
                    "cantidad": item.cantidad,
                    "precio_snapshot": producto.precio,
                    "personalizacion": item.personalizacion.excluidos,
                })
            
            # 2. Generar snapshot de dirección
            direccion = await self.uow.direcciones.get_by_id(direccion_id)
            if not direccion:
                raise DireccionNotFound()
            direccion_snapshot = {
                "calle": direccion.calle,
                "numero": direccion.numero,
                "departamento": direccion.departamento,
                "ciudad": direccion.ciudad,
                "provincia": direccion.provincia,
                "codigo_postal": direccion.codigo_postal,
            }
            
            # 3. Calcular total
            total = sum(d["cantidad"] * d["precio_snapshot"] for d in detalles_snapshot)
            
            # 4. Crear Pedido
            pedido = Pedido(
                cliente_id=cliente_id,
                estado_id=1,  # PENDIENTE
                direccion_snapshot=json.dumps(direccion_snapshot),
                total=total,
            )
            pedido = await self.uow.pedidos.create(pedido)
            
            # 5. Crear DetallePedido items
            for detalle in detalles_snapshot:
                detalle_pedido = DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=detalle["producto_id"],
                    cantidad=detalle["cantidad"],
                    precio_snapshot=detalle["precio_snapshot"],
                    personalizacion=detalle["personalizacion"],
                )
                await self.uow.detalles_pedido.create(detalle_pedido)
            
            # 6. Crear HistorialEstadoPedido (inicial)
            historial = HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_anterior_id=None,
                estado_nuevo_id=1,  # PENDIENTE
                usuario_id=cliente_id,
                timestamp=datetime.utcnow(),
                observacion="Pedido creado",
            )
            await self.uow.historial_estado.create(historial)
            
            # UoW commit aquí
            await self.uow.commit()
        
        return PedidoResponse.from_orm(pedido)
    
    async def list_orders(
        self, 
        cliente_id: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[PedidoResponse]:
        """Listar pedidos del cliente autenticado."""
        return await self.uow.pedidos.list_all(
            skip=skip, 
            limit=limit, 
            filters={"cliente_id": cliente_id},
        )
    
    async def get_order_detail(self, pedido_id: str, cliente_id: str) -> PedidoDetailResponse:
        """Obtener detalles de un pedido (con validación de ownership)."""
        pedido = await self.uow.pedidos.get_by_id(pedido_id)
        if not pedido or pedido.cliente_id != cliente_id:
            raise PedidoNotFound()
        
        detalles = await self.uow.detalles_pedido.list_all(
            filters={"pedido_id": pedido_id}
        )
        historial = await self.uow.historial_estado.list_all(
            filters={"pedido_id": pedido_id},
            order_by="timestamp ASC",
        )
        
        return PedidoDetailResponse(
            pedido=pedido,
            detalles=detalles,
            historial=historial,
        )
```

### Transactional Flow

```
POST /api/v1/pedidos
│
├─ Authenticate (get_current_user)
├─ Validate carrito_dto
├─ UoW.begin()
│  ├─ SELECT productos FOR UPDATE WHERE id IN (...)
│  ├─ Validate stock > cantidad for each
│  ├─ Build snapshots
│  ├─ INSERT pedido
│  ├─ INSERT detalles_pedido (N rows)
│  ├─ INSERT historial_estado_pedido
│  └─ COMMIT
└─ Return 201 Created + pedido
   
If ANY step fails → ROLLBACK
```

## Data Models (Pydantic Schemas)

```python
# Request
class CartItemDTO(BaseModel):
    producto_id: str
    cantidad: int
    personalizacion: PersonalizacionDTO

class PersonalizacionDTO(BaseModel):
    excluidos: List[int] = []

class CartCreateDTO(BaseModel):
    items: List[CartItemDTO]
    direccion_id: str

# Response
class DetallePedidoResponse(BaseModel):
    id: str
    cantidad: int
    precio_snapshot: float
    personalizacion: List[int]
    producto: ProductoMinimalResponse

class PedidoResponse(BaseModel):
    id: str
    cliente_id: str
    estado_id: int
    total: float
    creado_en: datetime

class PedidoDetailResponse(BaseModel):
    id: str
    cliente_id: str
    estado_id: int
    direccion_snapshot: dict
    total: float
    detalles: List[DetallePedidoResponse]
    historial: List[HistorialResponse]
    creado_en: datetime
```

## Validation Rules

- Carrito no puede estar vacío
- Cantidad debe ser > 0
- Personalización (excluidos) solo de ingredientes existentes en el producto
- Stock suficiente (validado en transacción con SELECT FOR UPDATE)
- Dirección debe existir y pertenecer al cliente
- Cliente debe estar autenticado (JWT válido)

## Error Handling (RFC 7807)

```
ProductoNotFound → 404
StockInsufficient → 400 Bad Request
DireccionNotFound → 404
CartEmptyError → 400 Bad Request
InvalidJWT → 401 Unauthorized
```
