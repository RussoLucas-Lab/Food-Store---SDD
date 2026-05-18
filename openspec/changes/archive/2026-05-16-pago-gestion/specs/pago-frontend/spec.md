## ADDED Requirements

### Requirement: PaymentPage muestra formulario de pago MP Brick
El sistema SHALL renderizar una `PaymentPage` en `features/pedidos/pages/` que use el componente `@mercadopago/sdk-react` (Checkout Bricks) para que el cliente ingrese datos de tarjeta. Los datos de tarjeta NUNCA deben enviarse al servidor (PCI DSS SAQ-A).

#### Scenario: Cliente accede a PaymentPage con pedido válido
- **WHEN** el cliente es redirigido a `/pedidos/{id}/pago` tras crear un pedido
- **THEN** la página muestra el resumen del pedido (total) y el formulario MP Brick inicializado con `VITE_MP_PUBLIC_KEY`

#### Scenario: Pago exitoso en frontend
- **WHEN** el cliente completa el formulario MP Brick y el backend retorna `status: "approved"` o `"pending"`
- **THEN** `paymentStore` se actualiza con `{ status, mpPaymentId }`, se limpia el carrito, y el usuario es redirigido a `/pedidos/{id}` con mensaje de confirmación

#### Scenario: Error en el pago
- **WHEN** el backend retorna error o el Brick reporta fallo
- **THEN** `paymentStore` registra el error, se muestra toast de error, el usuario puede reintentar sin abandonar la página

### Requirement: paymentStore gestiona el estado del proceso de pago
El sistema SHALL implementar un store Zustand `paymentStore` en `shared/stores/paymentStore.ts` sin persistencia en localStorage. Gestiona: `{ status: string | null, mpPaymentId: string | null, pedidoId: string | null, error: string | null }`.

#### Scenario: Estado inicial limpio
- **WHEN** el usuario navega a PaymentPage
- **THEN** `paymentStore` tiene todos los campos en `null` (estado vacío, sin persistencia de sesiones anteriores)

#### Scenario: Reset al salir de PaymentPage
- **WHEN** el usuario navega fuera de PaymentPage (cancelar, volver al inicio)
- **THEN** `paymentStore.reset()` limpia todos los campos a `null`

### Requirement: CheckoutPage redirige a PaymentPage tras crear pedido
El sistema SHALL, tras recibir 201 de `POST /api/v1/pedidos`, redirigir al cliente a `/pedidos/{id}/pago` en lugar de `/pedidos/{id}` directamente.

#### Scenario: Pedido creado exitosamente desde CheckoutPage
- **WHEN** `CreateOrderButton` recibe respuesta 201 con `{ id }`
- **THEN** el router navega a `/pedidos/{id}/pago` pasando el `pedidoId` al `paymentStore`
