# Spec: Creación de Pedidos (Backend Transaccional)

## Overview
Crear un pedido es una operación ATÓMICA (Unit of Work). Valida stock, genera snapshots de precios y dirección, crea registros en tablas pedidos, detalles_pedido, e historial_estado_pedido. Todo o nada.

## Capabilities

### cap-pedido-create-atomic
- Endpoint: POST /api/v1/pedidos
- Auth: JWT válido (get_current_user)
- Input: CartCreateDTO { items: [{producto_id, cantidad, personalizacion}], direccion_id }
- Process (en transacción con UoW):
  1. Validar carrito no vacío
  2. Para cada item:
     - SELECT producto FOR UPDATE (lock row)
     - Validar producto existe y stock >= cantidad
     - Generar snapshot: {producto_id, cantidad, precio_snapshot, personalizacion}
  3. SELECT direccion para snapshot (dirección debe existir y pertenecer a cliente)
  4. Calcular total = suma(cantidad * precio_snapshot)
  5. INSERT pedido {cliente_id, estado_id=1 (PENDIENTE), total, direccion_snapshot}
  6. Para cada item snapshot:
     - INSERT detalle_pedido {pedido_id, producto_id, cantidad, precio_snapshot, personalizacion}
  7. INSERT historial_estado_pedido {pedido_id, estado_nuevo_id=1, usuario_id, timestamp, observacion="Pedido creado"}
  8. COMMIT (rollback en cualquier error)
- Output: PedidoResponse { id, cliente_id, estado_id, total, creado_en }
- Errors:
  - 400 CartEmpty: carrito sin items
  - 404 ProductoNotFound
  - 400 StockInsufficient
  - 404 DireccionNotFound
  - 401 Unauthorized (JWT inválido)

### cap-pedido-validate-stock
- Dentro de transacción: SELECT productos FOR UPDATE
- Validar: stock >= cantidad para todos los productos
- Si falla alguno: rollback de toda la transacción
- No decrementar stock aún (se hace en cambio de estado a CONFIRMADO)

### cap-pedido-generar-snapshots
- Snapshot de precio: tomar producto.precio en el momento
- Snapshot de dirección: tomar dirección.* completa
- Almacenar como JSON en BD (direccion_snapshot, precio_snapshot)
- Garantía: cambios futuros en productos/direcciones NO afectan pedidos existentes

### cap-pedido-listado
- Endpoint: GET /api/v1/pedidos?skip=0&limit=10
- Auth: JWT válido
- Listar pedidos del cliente autenticado (cliente_id == user.id)
- Output: List[PedidoResponse]
- Ordenar por creado_en DESC (más recientes primero)
- Soportar paginación

### cap-pedido-detalle
- Endpoint: GET /api/v1/pedidos/{id}
- Auth: JWT válido
- Validar ownership: pedido.cliente_id == user.id (lanzar 403 Forbidden si no)
- Retornar:
  ```
  {
    id,
    cliente_id,
    estado_id,
    direccion_snapshot: {...},
    total,
    detalles: [
      {
        id,
        cantidad,
        precio_snapshot,
        personalizacion,
        producto: { id, nombre, precio }
      }
    ],
    historial: [
      { estado_anterior_id, estado_nuevo_id, usuario_id, timestamp, observacion }
    ],
    creado_en,
    actualizado_en
  }
  ```

## Data Models

### Tabla: pedidos

```sql
CREATE TABLE pedidos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cliente_id UUID NOT NULL REFERENCES usuarios(id),
  estado_id INT NOT NULL REFERENCES estado_pedido(id) DEFAULT 1,
  direccion_snapshot JSONB NOT NULL,
  total NUMERIC(12,2) NOT NULL,
  creado_en TIMESTAMP DEFAULT NOW(),
  actualizado_en TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT total_positive CHECK (total > 0),
  CONSTRAINT stock_positive CHECK (cantidad > 0)
);

CREATE INDEX idx_pedidos_cliente_id ON pedidos(cliente_id);
CREATE INDEX idx_pedidos_estado_id ON pedidos(estado_id);
```

### Tabla: detalles_pedido

```sql
CREATE TABLE detalles_pedido (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pedido_id UUID NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
  producto_id UUID NOT NULL REFERENCES productos(id),
  cantidad INT NOT NULL,
  precio_snapshot NUMERIC(12,2) NOT NULL,
  personalizacion INTEGER[] DEFAULT '{}',
  creado_en TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT cantidad_positive CHECK (cantidad > 0),
  CONSTRAINT precio_positive CHECK (precio_snapshot > 0)
);

CREATE INDEX idx_detalles_pedido_id ON detalles_pedido(pedido_id);
```

### Tabla: historial_estado_pedido (append-only)

```sql
CREATE TABLE historial_estado_pedido (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pedido_id UUID NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
  estado_anterior_id INT REFERENCES estado_pedido(id),
  estado_nuevo_id INT NOT NULL REFERENCES estado_pedido(id),
  usuario_id UUID REFERENCES usuarios(id),
  timestamp TIMESTAMP DEFAULT NOW(),
  observacion TEXT,
  
  CONSTRAINT no_update CHECK (true)  -- philosophical: tell devs not to update
);

CREATE INDEX idx_historial_pedido_id ON historial_estado_pedido(pedido_id);
```

## Pydantic Schemas

```python
class CartItemDTO(BaseModel):
    producto_id: str
    cantidad: int
    personalizacion: list[int] = []

class CartCreateDTO(BaseModel):
    items: list[CartItemDTO]
    direccion_id: str
    
    @validator('items')
    def items_not_empty(cls, v):
        if not v:
            raise ValueError('Carrito vacío')
        return v

class DetallePedidoResponse(BaseModel):
    id: str
    cantidad: int
    precio_snapshot: float
    personalizacion: list[int]
    
    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: str
    cliente_id: str
    estado_id: int
    total: float
    creado_en: datetime
    
    class Config:
        from_attributes = True

class PedidoDetailResponse(BaseModel):
    id: str
    cliente_id: str
    estado_id: int
    direccion_snapshot: dict
    total: float
    detalles: list[DetallePedidoResponse]
    historial: list[dict]  # [{estado_anterior, estado_nuevo, usuario, timestamp}]
    creado_en: datetime
```

## Transactional Guarantees

- **Atomicidad**: Usar UoW (async context manager) para begin/commit/rollback
- **Aislamiento**: SELECT FOR UPDATE en productos para evitar race conditions
- **Consistencia**: Validar todas las constraints (stock, amounts, FKs) antes de INSERT
- **Durabilidad**: PostgreSQL guarantees

## Testing

- [ ] Crear pedido con carrito válido
- [ ] Crear pedido incrementa pedidos.id
- [ ] Snapshot de precio es inmutable (cambios posteriores no lo afectan)
- [ ] Stock insuficiente → rollback
- [ ] Dirección inválida → 404
- [ ] Cliente no propietario → 403
- [ ] Listar pedidos solo del cliente autenticado
- [ ] Historial_estado_pedido tiene registro inicial
- [ ] Transacción rollback si falla en cualquier paso
