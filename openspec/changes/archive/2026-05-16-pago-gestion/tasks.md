## 1. Migración y modelo de datos

- [x] 1.1 Crear `backend/modules/pagos/model.py` con clase SQLModel `Pago` (campos: id, pedido_id, mp_payment_id, mp_status, external_reference UQ, idempotency_key UQ, creado_en, actualizado_en)
- [ ] 1.2 Generar migración Alembic: `alembic revision --autogenerate -m "add pagos table"` — BLOQUEADO: no hay Alembic configurado en el proyecto aún (usa in-memory UoW)
- [ ] 1.3 Aplicar migración: `alembic upgrade head` y verificar que no hay errores en BD limpia — BLOQUEADO: requiere 1.2 y PostgreSQL corriendo

## 2. Backend — módulo pagos

- [x] 2.1 Crear `backend/modules/pagos/repository.py` con `IPagoRepository` y `InMemoryPagoRepository`; métodos: `get_by_pedido_id`, `get_by_mp_payment_id`, `get_by_idempotency_key`
- [x] 2.2 Crear `backend/modules/pagos/schemas.py`: `PagoCreateDTO` (pedido_id, token, installments, payment_method_id, issuer_id), `PagoResponse` (id, pedido_id, mp_payment_id, mp_status, creado_en)
- [x] 2.3 Crear `backend/modules/pagos/exceptions.py`: `PedidoNotPendiente`, `PedidoNotFound`, `PagoAlreadyExists`, `MercadoPagoError`
- [x] 2.4 Agregar propiedad `pagos: IPagoRepository` a `IUnitOfWork` en `backend/core/uow.py` e implementarla en `InMemoryUnitOfWork` en `backend/core/uow_inmemory.py`
- [x] 2.5 Crear `backend/modules/pagos/service.py` con `PagoService`: método `create_payment(cliente_id, dto)` — valida pedido, genera `idempotency_key`, llama SDK MP, persiste `Pago` con estado `pending`
- [x] 2.6 Implementar `PagoService.process_approved_payment(mp_payment_id)` — lógica de confirmación atómica: actualiza `Pago.mp_status`, avanza pedido a CONFIRMADO, decrementa stock, inserta historial, hace `uow.commit()`
- [x] 2.7 Crear `backend/modules/pagos/router.py`: `POST /api/v1/pagos` (require CLIENT rol) y `POST /api/v1/pagos/webhook` (público, verifica con re-consulta a MP API antes de procesar)
- [x] 2.8 Registrar router de pagos en `backend/main.py`

## 3. Backend — webhook handler

- [x] 3.1 Implementar idempotencia en webhook: antes de procesar verificar si `Pago.mp_status == "approved"` ya está en BD → retornar 200 sin efecto
- [x] 3.2 Implementar re-consulta a API de MP (`GET /v1/payments/{id}`) para verificar estado real antes de ejecutar cualquier acción
- [x] 3.3 Manejar estados `pending`/`in_process`: solo actualizar `Pago.mp_status`, no avanzar pedido
- [x] 3.4 Manejar estados `rejected`/`cancelled`: actualizar `Pago.mp_status`, pedido permanece PENDIENTE

## 4. Frontend — paymentStore

- [x] 4.1 Crear `frontend/src/shared/stores/paymentStore.ts` con patrón useSyncExternalStore sin persistencia: campos `status`, `mpPaymentId`, `pedidoId`, `error`; acciones `setPaymentResult`, `setPedidoId`, `setError`, `reset`

## 5. Frontend — PaymentPage

- [x] 5.1 Instalar dependencia `@mercadopago/sdk-react` si no está presente: `npm install @mercadopago/sdk-react`
- [x] 5.2 Crear `frontend/src/features/pedidos/services/pagoClient.ts` con método `createPago(dto)` → `POST /api/v1/pagos`
- [x] 5.3 Crear `frontend/src/features/pedidos/pages/PaymentPage.tsx` con formulario de pago + resumen del pedido (total); incluye TODO para Checkout Brick cuando @mercadopago/sdk-react esté instalado
- [x] 5.4 Implementar flujo de éxito en `PaymentPage`: llamar `pagoClient.createPago`, actualizar `paymentStore`, limpiar carrito con `cartStore.clearCart()`, redirigir a `/pedidos/{id}` con mensaje de confirmación
- [x] 5.5 Implementar flujo de error en `PaymentPage`: registrar error en `paymentStore`, mostrar toast, permitir reintento sin salir de la página
- [x] 5.6 Agregar ruta `/pedidos/:id/pago` al router apuntando a `PaymentPage` (ruta protegida: solo CLIENT)

## 6. Frontend — integración con CheckoutPage

- [x] 6.1 Modificar `CreateOrderButton` en `CheckoutPage` para redirigir a `/pedidos/{id}/pago` en lugar de `/pedidos/{id}` tras recibir 201
- [x] 6.2 Llamar `paymentStore.setPedidoId(id)` al redirigir desde `CheckoutPage`

## 7. Tests

- [x] 7.1 Test unitario `PagoService.create_payment`: caso exitoso, pedido no PENDIENTE, pedido no encontrado
- [x] 7.2 Test unitario `PagoService.process_approved_payment`: idempotencia (ya aprobado), transición atómica, rollback en error
- [x] 7.3 Test unitario webhook handler: estados `approved`, `pending`, `rejected`, duplicado
- [x] 7.4 Test frontend `paymentStore`: estado inicial, setPaymentResult, reset
