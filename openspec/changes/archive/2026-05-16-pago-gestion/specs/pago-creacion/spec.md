## ADDED Requirements

### Requirement: Cliente puede iniciar un pago para un pedido
El sistema SHALL permitir al cliente autenticado crear un pago MercadoPago asociado a un pedido en estado PENDIENTE. El backend genera un `idempotency_key` UUID y llama al SDK MP Python; devuelve al frontend el `mp_payment_id` y el token de pago.

#### Scenario: Pago creado exitosamente
- **WHEN** el cliente envía `POST /api/v1/pagos` con `{ pedido_id, token, installments, payment_method_id }`
- **THEN** el sistema crea un registro `Pago` con estado `pending`, retorna 201 con `{ pago_id, mp_payment_id, status }`

#### Scenario: Pedido no existe o no pertenece al cliente
- **WHEN** el cliente envía `POST /api/v1/pagos` con un `pedido_id` que no existe o pertenece a otro cliente
- **THEN** el sistema retorna 404 con RFC 7807

#### Scenario: Pedido no está en estado PENDIENTE
- **WHEN** el cliente intenta pagar un pedido en estado distinto de PENDIENTE (ej. CONFIRMADO, CANCELADO)
- **THEN** el sistema retorna 400 Bad Request con RFC 7807

#### Scenario: Idempotencia — pago duplicado
- **WHEN** el cliente envía `POST /api/v1/pagos` para un pedido que ya tiene un pago registrado con `idempotency_key`
- **THEN** el sistema retorna el pago existente sin crear uno nuevo (200 OK)

### Requirement: El modelo Pago almacena datos de auditoría
El sistema SHALL persistir en la tabla `pagos`: `id`, `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference` (UUID único), `idempotency_key` (UUID único), `creado_en`, `actualizado_en`.

#### Scenario: Campos únicos garantizados
- **WHEN** se intenta insertar un `Pago` con `external_reference` o `idempotency_key` duplicado
- **THEN** la base de datos rechaza la inserción con error de constraint UNIQUE
