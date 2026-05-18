## MODIFIED Requirements

### Requirement: Creación de pedido redirige al flujo de pago
Tras un `POST /api/v1/pedidos` exitoso, el frontend SHALL redirigir al cliente a `/pedidos/{id}/pago` para completar el proceso de pago, en lugar de navegar directamente al detalle del pedido. El pedido permanece en estado PENDIENTE hasta que el pago sea procesado.

#### Scenario: Pedido creado — redirección a PaymentPage
- **WHEN** `CreateOrderButton` recibe respuesta 201 con `{ id }` del endpoint de creación de pedido
- **THEN** el router navega a `/pedidos/{id}/pago` y `paymentStore.setPedidoId(id)` guarda el contexto de pago

#### Scenario: Error en creación de pedido — no redirige
- **WHEN** `POST /api/v1/pedidos` retorna error (400, 401, 422, 500)
- **THEN** se muestra toast de error en CheckoutPage y no hay navegación; el carrito no se limpia
