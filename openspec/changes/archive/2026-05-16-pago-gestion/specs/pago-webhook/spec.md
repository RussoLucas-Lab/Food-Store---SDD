## ADDED Requirements

### Requirement: El sistema procesa notificaciones IPN de MercadoPago
El sistema SHALL exponer `POST /api/v1/pagos/webhook` para recibir notificaciones IPN de MercadoPago. Tras recibir la notificación, el sistema MUST verificar el estado real del pago consultando la API de MP (nunca confiar solo en el payload entrante).

#### Scenario: Webhook recibido con estado approved
- **WHEN** MercadoPago envía un IPN con `mp_payment_id` de un pago en estado `approved`
- **THEN** el sistema verifica con la API de MP, actualiza `Pago.mp_status = "approved"`, ejecuta la transición atómica PENDIENTE→CONFIRMADO, decrementa stock, registra historial, y retorna 200 OK

#### Scenario: Webhook duplicado para pago ya aprobado
- **WHEN** MercadoPago envía un IPN para un `mp_payment_id` cuyo pago ya tiene `mp_status = "approved"` en BD
- **THEN** el sistema retorna 200 OK sin ejecutar ninguna transición ni modificar datos

#### Scenario: Webhook con estado pending o in_process
- **WHEN** MercadoPago envía un IPN con estado `pending` o `in_process`
- **THEN** el sistema actualiza `Pago.mp_status` y retorna 200 OK; el pedido permanece en PENDIENTE

#### Scenario: Webhook con estado rejected o cancelled
- **WHEN** MercadoPago envía un IPN con estado `rejected` o `cancelled`
- **THEN** el sistema actualiza `Pago.mp_status` y retorna 200 OK; el pedido permanece en PENDIENTE (el cliente puede reintentar)

#### Scenario: Webhook para pago desconocido
- **WHEN** MercadoPago envía un IPN con `mp_payment_id` que no existe en la tabla `pagos`
- **THEN** el sistema retorna 200 OK (no exponer información sobre pagos desconocidos)

### Requirement: Transición PENDIENTE→CONFIRMADO es atómica con decremento de stock
Al procesar un pago `approved`, el sistema MUST ejecutar en una sola transacción UoW: actualización de estado del pedido, decremento de stock de cada producto, e inserción en `historial_estado_pedido`.

#### Scenario: Stock suficiente al confirmar
- **WHEN** el pago es aprobado y todos los productos tienen stock suficiente
- **THEN** el sistema decrementa el stock de cada producto, avanza el pedido a CONFIRMADO, e inserta entrada en historial con `usuario_id = NULL` (transición de sistema)

#### Scenario: Fallo en transacción de confirmación
- **WHEN** ocurre cualquier error durante la transacción de confirmación (ej. stock insuficiente en race condition)
- **THEN** la transacción hace ROLLBACK completo; `Pago.mp_status` permanece sin el cambio; se registra el error en logs
