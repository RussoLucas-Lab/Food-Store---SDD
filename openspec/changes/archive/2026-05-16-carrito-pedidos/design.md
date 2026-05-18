## Architecture Overview

### Feature-First File Layout

```
backend/
├── core/
│   ├── uow.py                   ← IUnitOfWork: agrega props pedidos/detalles_pedido/historial_estado
│   └── uow_inmemory.py          ← InMemoryUnitOfWork: instancia repos de pedidos
└── modules/
    └── pedidos/                 ← TODO el dominio vive acá (feature-first)
        ├── model.py             ← Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum
        ├── repository.py        ← InMemoryPedidoRepository, InMemoryDetallePedidoRepository, InMemoryHistorialEstadoPedidoRepository
        ├── schemas.py           ← CartCreateDTO, CartItemDTO, PedidoResponse, PedidoDetailResponse
        ├── exceptions.py        ← CartEmptyError, StockInsufficient, PedidoNotFound, etc.
        ├── service.py           ← PedidoService (sync, llama self.uow.commit())
        └── router.py            ← APIRouter(prefix="/pedidos"), registrado en main.py con /api/v1

frontend/src/
├── shared/
│   └── stores/
│       └── cartStore.ts         ← Zustand + localStorage (estado del cliente)
└── features/
    └── pedidos/                 ← Feature FSD para checkout/pedidos
        ├── components/
        │   ├── CartItemList.tsx
        │   ├── CartSummary.tsx
        │   ├── DirectionSelector.tsx
        │   ├── CreateOrderButton.tsx
        │   └── OrderConfirmationModal.tsx
        ├── pages/
        │   └── CheckoutPage.tsx
        └── services/
            └── pedidoClient.ts  ← Métodos HTTP para /api/v1/pedidos
```

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND — features/pedidos/ (FSD)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CheckoutPage (features/pedidos/pages/CheckoutPage.tsx)          │
│  ├─ CartItemList   → lee shared/stores/cartStore.ts              │
│  ├─ CartSummary    → lee shared/stores/cartStore.ts              │
│  ├─ DirectionSelector → TanStack Query GET /clientes/me/dirs     │
│  └─ CreateOrderButton → pedidoClient.createPedido()             │
│                                                                   │
│  CartStore (shared/stores/cartStore.ts — Zustand + localStorage) │
│  ├─ items: CartItem[]                                            │
│  ├─ addItem / removeItem / updateQuantity / clearCart            │
│  ├─ getTotal(): number                                           │
│  └─ getCartDTO(): CartCreateDTO                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                    features/pedidos/services/pedidoClient.ts
                   POST /api/v1/pedidos { carrito }
                   GET  /api/v1/pedidos
                   GET  /api/v1/pedidos/{id}
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND — modules/pedidos/ (feature-first)          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  router.py  →  service.py  →  uow  →  repository.py             │
│                                                                   │
│  POST /api/v1/pedidos                                            │
│  ├─ require_role("client") [JWT auth]                           │
│  ├─ PedidoService.create_order(cliente_id, carrito_dto)          │
│  │  ├─ Validar items no vacío                                    │
│  │  ├─ Validar stock por producto                                │
│  │  ├─ Validar dirección (ownership del cliente)                 │
│  │  ├─ Capturar snapshots (nombre, precio, dirección)            │
│  │  ├─ uow.pedidos.create(Pedido)                                │
│  │  ├─ uow.detalles_pedido.create(DetallePedido) × N            │
│  │  ├─ uow.historial_estado.create(Historial inicial)           │
│  │  └─ uow.commit()                                              │
│  └─ Return 201 + PedidoResponse                                  │
│                                                                   │
│  GET /api/v1/pedidos                                             │
│  ├─ require_role("client")                                      │
│  ├─ PedidoService.list_orders(cliente_id, skip, limit)           │
│  └─ Return 200 + List[PedidoResponse]                            │
│                                                                   │
│  GET /api/v1/pedidos/{id}                                        │
│  ├─ require_role("client")                                      │
│  ├─ PedidoService.get_order_detail(pedido_id, cliente_id)        │
│  │  └─ Valida ownership → 403 si no coincide                     │
│  └─ Return 200 + PedidoDetailResponse                            │
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

> **Patrón del proyecto**: sync (sin async/await), llama `self.uow.commit()` después de mutaciones.
> Igual que `backend/modules/categorias/service.py`. NO usar context manager `async with self.uow`.
> Archivo: `backend/modules/pedidos/service.py`

```python
# backend/modules/pedidos/service.py
import json
from datetime import datetime
from typing import List
from backend.core.uow import IUnitOfWork
from .model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum
from .schemas import CartCreateDTO
from .exceptions import CartEmptyError, StockInsufficient, PedidoNotFound, UnauthorizedPedidoAccess, DireccionNotFound


class PedidoService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def create_order(self, cliente_id: int, carrito_dto: CartCreateDTO) -> dict:
        if not carrito_dto.items:
            raise CartEmptyError()

        # 1. Validar stock y capturar snapshots
        detalles_data = []
        for item in carrito_dto.items:
            producto = self.uow.productos.get_by_id(item.producto_id)
            if not producto:
                raise ValueError(f"Producto {item.producto_id} no encontrado")
            if producto.stock < item.cantidad:
                raise StockInsufficient(f"Stock insuficiente para {producto.nombre}")
            detalles_data.append({
                "producto_id": item.producto_id,
                "nombre_snapshot": producto.nombre,       # snapshot inmutable
                "precio_snapshot": producto.precio,       # snapshot inmutable
                "cantidad": item.cantidad,
                "personalizacion": item.personalizacion.excluidos,
            })

        # 2. Validar y capturar snapshot de dirección
        direccion = self.uow.clientes.get_direccion_by_id(carrito_dto.direccion_id)
        if not direccion or direccion.cliente_id != cliente_id:
            raise DireccionNotFound(carrito_dto.direccion_id)
        direccion_snapshot = json.dumps(direccion.to_dict())

        # 3. Calcular total
        total = sum(d["cantidad"] * d["precio_snapshot"] for d in detalles_data)

        # 4. Crear Pedido
        pedido = Pedido(
            cliente_id=cliente_id,
            estado=EstadoPedidoEnum.PENDIENTE,
            direccion_snapshot=direccion_snapshot,
            total=total,
        )
        pedido = self.uow.pedidos.create(pedido)

        # 5. Crear DetallePedido (con snapshots — inmutables)
        for d in detalles_data:
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=d["producto_id"],
                nombre_snapshot=d["nombre_snapshot"],
                precio_snapshot=d["precio_snapshot"],
                cantidad=d["cantidad"],
                personalizacion=d["personalizacion"],
            )
            self.uow.detalles_pedido.create(detalle)

        # 6. Registrar historial inicial (append-only)
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=None,
            estado_nuevo=EstadoPedidoEnum.PENDIENTE,
            usuario_id=cliente_id,
            observacion="Pedido creado",
        )
        self.uow.historial_estado.create(historial)

        self.uow.commit()
        return pedido.to_dict()

    def list_orders(self, cliente_id: int, skip: int = 0, limit: int = 10) -> List[dict]:
        pedidos = self.uow.pedidos.list_by_cliente(cliente_id, skip=skip, limit=limit)
        return [p.to_dict() for p in pedidos]

    def get_order_detail(self, pedido_id: int, cliente_id: int) -> dict:
        pedido = self.uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFound(pedido_id)
        if pedido.cliente_id != cliente_id:
            raise UnauthorizedPedidoAccess()

        detalles = self.uow.detalles_pedido.list_by_pedido(pedido_id)
        historial = self.uow.historial_estado.list_by_pedido(pedido_id)

        result = pedido.to_dict()
        result["detalles"] = [d.to_dict() for d in detalles]
        result["historial"] = [h.to_dict() for h in historial]
        return result
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
