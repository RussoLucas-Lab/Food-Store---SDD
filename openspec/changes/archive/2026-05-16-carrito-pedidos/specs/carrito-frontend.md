# Spec: Carrito Client-Side (Zustand + localStorage)

## Overview
El carrito es un store global en el frontend (Zustand) que persiste en localStorage. NO existe en el backend. Cada item contiene: producto_id, cantidad, y personalización (ingredientes excluidos).

## Capabilities

### cap-cart-store-init
- Al cargar la app, CartStore intenta cargar from localStorage
- Si no existe, inicia con items: []
- Sync automático: cada cambio en items se persiste en localStorage

### cap-cart-add-item
- Acción: `cartStore.addItem(producto, cantidad, excluidos: [])`
- Si producto_id ya existe en carrito:
  - Incrementar cantidad
  - Mergear excluidos (union de arrays)
- Si nuevo:
  - Crear nuevo CartItem
  - Appendear a items
- Guardar en localStorage

### cap-cart-update-quantity
- Acción: `cartStore.updateQuantity(producto_id, cantidad)`
- Si cantidad <= 0: remover item
- Sino: actualizar cantidad
- Guardar en localStorage

### cap-cart-remove-item
- Acción: `cartStore.removeItem(producto_id)`
- Remover item del array
- Guardar en localStorage

### cap-cart-get-total
- Acción: `cartStore.getTotal(): number`
- Calcular: suma de (cantidad * precio) de todos los items
- NOTA: precio viene del producto actual (no es snapshot, es para UI)

### cap-cart-clear
- Acción: `cartStore.clearCart()`
- Vaciar items array
- Limpiar localStorage

### cap-cart-serialize
- Acción: `cartStore.getCartDTO(): CartCreateDTO`
- Retornar estructura serializable para POST /pedidos

## Data Structure

```typescript
interface CartItem {
  producto_id: string;
  producto_nombre: string; // para mostrar en UI
  precio: number;           // precio actual (fetched)
  cantidad: number;
  personalizacion: {
    excluidos: number[]; // ingrediente_ids excluidos
  };
}

interface CartStore {
  items: CartItem[];
  addItem(producto: Producto, cantidad: number, excluidos?: number[]): void;
  updateQuantity(producto_id: string, cantidad: number): void;
  removeItem(producto_id: string): void;
  clearCart(): void;
  getTotal(): number;
  getCartDTO(): CartCreateDTO;
}
```

## localStorage Format

```json
{
  "food-store:cart": {
    "items": [
      {
        "producto_id": "123",
        "producto_nombre": "Pizza Mozzarella",
        "precio": 12.50,
        "cantidad": 2,
        "personalizacion": {
          "excluidos": [5, 7]
        }
      }
    ]
  }
}
```

## Error Handling

- Cantidad debe ser > 0
- Producto no puede agregarse si no existe (validar antes de llamar addItem)
- Si localStorage falla (ej: cuota llena), loguear warning pero no crashear

## Testing

- [ ] addItem agrega nuevo item
- [ ] addItem incrementa cantidad si existe
- [ ] updateQuantity mergeará excluidos correctamente
- [ ] removeItem elimina item
- [ ] clearCart vacía todo
- [ ] getTotal calcula suma correcta
- [ ] localStorage persiste y se carga al refresh
- [ ] getCartDTO retorna estructura válida
