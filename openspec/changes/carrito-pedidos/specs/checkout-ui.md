# Spec: Checkout UI (React Components)

## Overview
CheckoutPage es la página donde el usuario revisa su carrito, selecciona una dirección de entrega, y crea el pedido. Consiste en: CartItemList, CartSummary, DirectionSelector, y CreateOrderButton.

## Capabilities

### cap-checkout-page-render
- Ruta: `/checkout` (protegida, requiere autenticación)
- Layout:
  ```
  CheckoutPage
  ├─ Header: "Confirmar Compra"
  ├─ Main Content (2 columns en desktop, 1 en mobile):
  │  ├─ Left: CartItemList
  │  ├─ Divider
  │  └─ Right: CartSummary + DirectionSelector + CreateOrderButton
  └─ Footer: navigation
  ```
- Load direcciones: GET /api/v1/clientes/me/direcciones
- Load carrito: from cartStore
- Error handling: si no hay carrito, mostrar mensaje "Carrito vacío"

### cap-cart-item-list
- Componente: `<CartItemList />`
- Prop: items from cartStore.getState().items
- Para cada item:
  ```
  ┌──────────────────────────────────────┐
  │ [img] Nombre Producto                │
  │ Cantidad: 2 × $12.50 = $25.00        │
  │ Excluidos: Cebolla, Ajo              │
  │ [- ] [ qty input ] [+] [🗑️ Remover]  │
  └──────────────────────────────────────┘
  ```
- Acciones:
  - Click `-`: cartStore.updateQuantity(producto_id, qty - 1)
  - Click `+`: cartStore.updateQuantity(producto_id, qty + 1)
  - Click `🗑️`: cartStore.removeItem(producto_id)
- Qty input debe ser > 0
- Si qty se vuelve 0, remover item

### cap-cart-summary
- Componente: `<CartSummary />`
- Mostrar:
  ```
  ┌──────────────────────────────┐
  │ RESUMEN                      │
  ├──────────────────────────────┤
  │ Subtotal:     $XX.XX         │
  │ Envío:        $ 5.00 (fijo)  │
  ├──────────────────────────────┤
  │ TOTAL:        $XX.XX         │
  └──────────────────────────────┘
  ```
- Subtotal = cartStore.getTotal()
- Envío = hardcoded $5.00 (en el futuro será variable)
- Total = Subtotal + Envío
- Auto-update si carrito cambia

### cap-direction-selector
- Componente: `<DirectionSelector />`
- Cargar direcciones: GET /api/v1/clientes/me/direcciones
- Mostrar:
  ```
  ┌─────────────────────────────────────┐
  │ Dirección de Entrega                │
  ├─────────────────────────────────────┤
  │ ○ [Default] Calle 123, Apt 5        │
  │ ○ Calle 456, Apt 10                 │
  │ ○ Calle 789, Apt 2                  │
  │ [+ Agregar Nueva Dirección]         │
  └─────────────────────────────────────┘
  ```
- State: selectedDirectionId
- Radio buttons para seleccionar
- Al seleccionar: setSelectedDirectionId(id)
- Link "+ Agregar..." navega a /clientes/direcciones/nueva
- Button "Crear Pedido" se habilita solo si hay dirección seleccionada

### cap-create-order-button
- Componente: `<CreateOrderButton />`
- Disabled state:
  - Si carrito está vacío
  - Si no hay dirección seleccionada
  - Si está en loading
- Click action:
  ```
  POST /api/v1/pedidos {
    items: cartStore.getCartDTO().items,
    direccion_id: selectedDirectionId
  }
  ```
- Loading: mostrar spinner, disable button
- Success:
  - cartStore.clearCart()
  - navigate(`/pedidos/${pedidoId}`)
  - show toast "Pedido creado exitosamente"
- Error:
  - show error toast con mensaje from API
  - keep button enabled para reintentar

### cap-order-confirmation-modal
- Componente: `<OrderConfirmationModal />`
- Trigger: después de crear pedido exitosamente
- Content:
  ```
  ┌──────────────────────────────┐
  │ ✓ Pedido Creado              │
  │                              │
  │ ID: abc123def456...          │
  │ Total: $XX.XX                │
  │ Estado: Pendiente de Pago    │
  │                              │
  │ [Ver Pedido] [Continuar]     │
  └──────────────────────────────┘
  ```
- Buttons:
  - "Ver Pedido": navigate(/pedidos/{id})
  - "Continuar": navigate(/catalogo), cerrar modal

## Data Flow

```
CheckoutPage mounts
├─ useQuery: GET /api/v1/clientes/me/direcciones
├─ cartStore.getState(): leer items
├─ Render: CartItemList + CartSummary + DirectionSelector
│
User clicks "Crear Pedido"
├─ Validar: carrito no vacío && dirección seleccionada
├─ useMutation: POST /api/v1/pedidos
├─ On success:
│  ├─ cartStore.clearCart()
│  ├─ navigate(/pedidos/{id})
│  └─ show ConfirmationModal
└─ On error: show error toast
```

## Error Handling

- Carrito vacío → disable button, mostrar hint
- Dirección no seleccionada → disable button
- API 400 → show error toast (stock insuficiente, etc.)
- API 401 → redirect a login
- API 404 → mostrar "Dirección no existe"

## Accessibility

- Labels for all inputs
- ARIA roles for custom components (listbox, radio, etc.)
- Keyboard navigation: Tab, Enter, Arrow keys
- Focus management: focus button after modal close

## Mobile Responsive

- Desktop: 2-column layout
- Tablet: 1-column stacked
- Mobile: 1-column, touch-friendly buttons

## Testing

- [ ] CheckoutPage renders sin errores
- [ ] CartItemList muestra items del carrito
- [ ] UpdateQuantity actualiza cartStore
- [ ] RemoveItem quita item
- [ ] DirectionSelector carga direcciones
- [ ] CartSummary calcula total correcto (subtotal + envío)
- [ ] CreateOrderButton disabled si carrito vacío
- [ ] CreateOrderButton disabled si no hay dirección
- [ ] POST /api/v1/pedidos called con carrito correcto
- [ ] Success: cartStore cleared, navegación a pedido
- [ ] Error: error toast mostrado, button sigue enabled
