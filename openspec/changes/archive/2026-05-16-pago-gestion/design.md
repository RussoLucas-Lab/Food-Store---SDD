## Context

El módulo `pedidos` crea pedidos en estado PENDIENTE pero no tiene mecanismo de cobro. El stack ya incluye SDK MercadoPago Python (backend) y `@mercadopago/sdk-react` (frontend). El flujo debe cumplir PCI DSS SAQ-A: los datos de tarjeta nunca tocan el servidor (tokenización en browser). El backend ya usa el patrón Repository + Unit of Work con sync (no async/await), y sigue arquitectura feature-first en `backend/modules/`.

## Goals / Non-Goals

**Goals:**
- Implementar el flujo completo de pago: creación → webhook → confirmación atómica de pedido + stock.
- Garantizar idempotencia en creación de pagos y procesamiento de webhooks.
- Mantener PCI DSS SAQ-A: tarjeta tokenizada en browser, backend solo recibe `token`.
- Registrar estado del proceso de pago en `paymentStore` Zustand (sin persistencia).
- Migración Alembic para tabla `pagos`.

**Non-Goals:**
- Gestión de devoluciones/reembolsos (fuera de scope para este change).
- Panel admin de pagos (cubierto en `administracion-general`).
- Pagos con métodos no MP (efectivo/transferencia no requieren este flujo).

## Decisions

### D1: Verificación de webhook con re-consulta a MP API

El handler de webhook NO confía solo en el payload entrante. Tras recibir el IPN, hace `GET /v1/payments/{id}` a la API de MP para verificar el estado real.

**Alternativa descartada**: confiar directamente en el payload → vulnerable a webhooks falsificados o desactualizados.

**Rationale**: recomendación explícita de MP y del CLAUDE.md del proyecto.

### D2: Idempotencia doble — `idempotency_key` + dedup en webhook

Cada pago tiene `idempotency_key` UUID v4 generado en backend al crear el pago. El handler de webhook verifica si `mp_payment_id` ya fue procesado (estado `approved`) antes de ejecutar la transición; si ya está, retorna 200 sin efecto.

**Rationale**: webhooks de MP pueden llegar duplicados o fuera de orden.

### D3: Módulo feature-first `backend/modules/pagos/`

Sigue exactamente el mismo patrón que `pedidos/`: model → repository → schemas → service → router. `core/uow.py` agrega la propiedad `pagos: IPagoRepository`.

**Alternativa descartada**: agregar lógica de pago dentro de `pedidos/service.py` → viola SRP y mezcla dominios.

### D4: Transición PENDIENTE→CONFIRMADO + stock en una sola UoW

`PagoService.process_approved_payment()` abre una transacción que:
1. Marca el pago como `approved` en BD.
2. Actualiza `pedido.estado` a CONFIRMADO.
3. Decrementa stock de cada producto (SELECT FOR UPDATE).
4. Registra entrada en `historial_estado_pedido` (append-only).
5. Hace `uow.commit()` una sola vez.

Si cualquier paso falla → ROLLBACK completo.

**Rationale**: atomicidad requerida por RN-FS03 (CLAUDE.md).

### D5: Frontend usa MP Checkout Bricks (no Checkout Pro redirect)

El cliente paga sin salir de la SPA. `PaymentPage` renderiza el Brick de pago de `@mercadopago/sdk-react`. El token resultante se envía al backend vía `POST /api/v1/pagos`.

**Alternativa descartada**: Checkout Pro (redirect externo) → UX disruptiva, no permite control del flujo post-pago en la SPA.

### D6: `paymentStore` Zustand sin persistencia

Gestiona `{ status, mpPaymentId, pedidoId, error }`. No se persiste en localStorage porque el estado de pago es efímero y no debe sobrevivir recargas (el usuario debe reiniciar si la sesión se interrumpe).

## Risks / Trade-offs

- [Webhook no llega] → El pedido queda en PENDIENTE indefinidamente. Mitigación: UI muestra estado pendiente con opción de consultar estado manualmente (botón "verificar pago"). Alcance futuro: polling o long-polling.
- [MP devuelve `pending` antes de `approved`] → El pedido no avanza. El webhook llegará cuando MP procese. El usuario ve estado "pago en proceso".
- [Stock race condition] → Mitigado con SELECT FOR UPDATE en la transacción de confirmación.
- [idempotency_key colisión] → UUID v4 tiene probabilidad de colisión negligible; aun así, la columna tiene constraint UNIQUE y la inserción fallará con error manejado.

## Migration Plan

1. Crear `backend/modules/pagos/model.py` con clase `Pago`.
2. Generar migración: `alembic revision --autogenerate -m "add pagos table"`.
3. Aplicar: `alembic upgrade head`.
4. El seed existente no requiere cambios (no hay datos iniciales de pagos).
5. Rollback: `alembic downgrade -1` elimina la tabla `pagos`.

## Open Questions

- ¿El webhook de MP es alcanzable en desarrollo local? → Requiere ngrok o similar. Para tests, mockear el SDK de MP.
- ¿Se implementa el botón "verificar pago" (polling manual) en este change o se deja para `frontend-ajustes-finales`? → Por ahora se deja pendiente; la UI solo muestra el estado actual del pedido.
