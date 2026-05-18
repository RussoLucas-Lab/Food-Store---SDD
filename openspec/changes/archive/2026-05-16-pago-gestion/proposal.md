## Why

Los pedidos se crean en estado PENDIENTE pero no tienen mecanismo de cobro: sin integración de pagos el e-commerce no puede completar transacciones ni avanzar el ciclo de vida del pedido. Este change conecta el flujo de carrito-pedidos con MercadoPago para que el cliente pueda pagar y el sistema confirme el pedido automáticamente.

## What Changes

- Nuevo módulo backend `backend/modules/pagos/` con modelo `Pago`, servicio de creación de pago MP y handler de webhook IPN.
- Nueva ruta `POST /api/v1/pagos` para iniciar un pago asociado a un pedido.
- Nueva ruta `POST /api/v1/pagos/webhook` para recibir notificaciones IPN de MercadoPago.
- Al recibir un webhook `approved`: transición atómica PENDIENTE → CONFIRMADO + decremento de stock (UoW).
- Nuevo `paymentStore` Zustand (sin persistencia) para gestionar el estado del proceso de pago en el frontend.
- Nueva página `PaymentPage` en `features/pedidos/` con formulario MP Brick (tokenización en browser, sin datos de tarjeta en servidor).
- Idempotencia garantizada: `idempotency_key` UUID por pago; webhooks duplicados se ignoran.
- Migración Alembic: tabla `pagos`.

## Capabilities

### New Capabilities

- `pago-creacion`: Creación de pago MP desde backend — genera `idempotency_key`, llama SDK MP, devuelve `payment_id` y `init_point` al frontend.
- `pago-webhook`: Handler IPN que verifica estado real con MP API, ejecuta transición PENDIENTE→CONFIRMADO con decremento atómico de stock al recibir `approved`.
- `pago-frontend`: Formulario de pago con MP Brick (Checkout Bricks), `paymentStore` Zustand, y flujo completo en `PaymentPage`.

### Modified Capabilities

- `pedido-creacion`: El flujo de creación de pedido ahora incluye la ruta al pago (redirect a PaymentPage tras crear pedido exitoso).

## Impact

- **Backend**: nuevo módulo `backend/modules/pagos/` (model, repo, schemas, service, router). `core/uow.py` agrega prop `pagos`. `main.py` registra el router. Migración Alembic.
- **Frontend**: nueva `PaymentPage` en `features/pedidos/pages/`, nuevo `paymentStore` en `shared/stores/`, dependencia `@mercadopago/sdk-react`. `CheckoutPage` redirige a `PaymentPage` en lugar de `/pedidos/{id}` directamente.
- **Variables de entorno**: `MP_ACCESS_TOKEN`, `MP_PUBLIC_KEY`, `MP_NOTIFICATION_URL` ya documentadas; deben estar presentes.
- **Dependencias externas**: SDK Python `mercadopago`, SDK frontend `@mercadopago/sdk-react`.
