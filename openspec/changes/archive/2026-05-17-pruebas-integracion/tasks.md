## 1. Setup e infraestructura

- [x] 1.1 Agregar `pytest-cov>=4.0` y `httpx>=0.27` a `backend/requirements.txt`
- [x] 1.2 Crear `pytest.ini` en la raíz con `addopts`, markers (`unit`, `integration`) y `--cov-fail-under=60`
- [x] 1.3 Crear `Makefile` en la raíz con targets `test`, `test-cov` y `test-integration`
- [x] 1.4 Agregar `htmlcov/` y `.coverage` a `.gitignore`

## 2. Tests unitarios — módulo productos — Service

- [x] 2.1 Crear `backend/tests/modules/productos/conftest.py` con fixtures de `ProductService` usando mock UoW
- [x] 2.2 Crear `test_producto_service.py`: test crear producto con datos válidos → producto retornado
- [x] 2.3 Test: crear producto sin `category_ids` lanza `ValueError`
- [x] 2.4 Test: crear producto sin `ingredients` lanza `ValueError`
- [x] 2.5 Test: crear producto con `base_price <= 0` lanza `ValueError`
- [x] 2.6 Test: `calculate_product_stock` con ingrediente disponible calcula stock correctamente
- [x] 2.7 Test: `deactivate_product` llama soft_delete y commit (método agregado a ProductService)

## 3. Tests unitarios — módulo productos — Endpoints

- [x] 3.1 Crear `test_producto_endpoints.py` con `TestClient` de FastAPI
- [x] 3.2 Test: `GET /productos` sin auth retorna HTTP 200 con lista
- [x] 3.3 Test: `GET /productos/{id}` con id existente retorna HTTP 200
- [x] 3.4 Test: `GET /productos/{id}` con id inexistente retorna HTTP 404
- [x] 3.5 Test: `POST /productos` sin token retorna HTTP 401 o 403
- [x] 3.6 Test: `POST /productos` con token ADMIN y payload válido retorna HTTP 201

## 4. Infraestructura de integración

- [x] 4.1 Crear `backend/tests/integration/__init__.py`
- [x] 4.2 No aplica (no hay SQLite/SQLModel — in-memory UoW ya provee aislamiento)
- [x] 4.3 No aplica (rollback gestionado por reset_all_repos autouse en conftest global)
- [x] 4.4 No aplica (no se requiere override de dependencia FastAPI — singleton_uow es compartido)
- [x] 4.5 Fixture `client` con `TestClient(app)` creada en `backend/tests/integration/conftest.py`
- [x] 4.6 Fixtures `admin_headers`, `client_headers`, `pedidos_headers` con JWT por rol

## 5. Tests de integración — Autenticación

- [x] 5.1 Crear `backend/tests/integration/test_auth_flow.py` marcado con `@pytest.mark.integration`
- [x] 5.2 Test: `POST /auth/register` con datos válidos retorna HTTP 201
- [x] 5.3 Test: `POST /auth/login` con credenciales válidas retorna `access_token` y `refresh_token`
- [x] 5.4 Test: endpoint protegido sin Authorization header retorna HTTP 401
- [x] 5.5 Test: endpoint protegido con Bearer token válido retorna HTTP 200

## 6. Tests de integración — Catálogo

- [x] 6.1 Crear `backend/tests/integration/test_catalogo_flow.py` marcado con `@pytest.mark.integration`
- [x] 6.2 Test: `GET /productos` sin auth retorna HTTP 200
- [x] 6.3 Test: `POST /productos` como ADMIN retorna HTTP 201 y el producto aparece en GET
- [x] 6.4 Test: `POST /productos` como CLIENT retorna HTTP 403

## 7. Tests de integración — Pedidos

- [x] 7.1 Crear `backend/tests/integration/test_pedido_flow.py` marcado con `@pytest.mark.integration`
- [x] 7.2 Test: cliente autenticado crea pedido con producto disponible → HTTP 201, estado PENDIENTE
- [x] 7.3 Test: cliente crea pedido con cantidad mayor al stock → HTTP 400 o 422
- [x] 7.4 Test: `GET /api/v1/pedidos` retorna solo los pedidos del cliente autenticado

## 8. Tests de integración — Webhook de pago

- [x] 8.1 Crear `backend/tests/integration/test_pago_flow.py` marcado con `@pytest.mark.integration`
- [x] 8.2 Test: `process_approved_payment` transiciona pedido a CONFIRMADO e inserta historial
- [x] 8.3 Test: webhook duplicado (mismo `mp_payment_id`) retorna True sin duplicar pago ni transición
- [x] 8.4 Test: `update_payment_status(rejected)` deja el pedido en PENDIENTE

## 9. Tests de integración — Transición de estados

- [x] 9.1 Crear `backend/tests/integration/test_despacho_flow.py` marcado con `@pytest.mark.integration`
- [x] 9.2 Test: usuario PEDIDOS avanza pedido de CONFIRMADO a EN_PREP → HTTP 200
- [x] 9.3 Test: usuario CLIENT intenta avanzar estado → HTTP 403
- [x] 9.4 Test: ADMIN cancela pedido CONFIRMADO → estado CANCELADO y stock restaurado
- [x] 9.5 Test: intentar cancelar pedido ENTREGADO → HTTP 409 (transición inválida)

## 10. Validación de cobertura

- [x] 10.1 Correr tests y verificar que la cobertura supera el 60% — **RESULTADO: 75%**
- [x] 10.2 Revisar reporte HTML en `htmlcov/index.html` — disponible tras `make test-cov`
- [x] 10.3 Cobertura total 75% > 60% — no se requieren tests adicionales
