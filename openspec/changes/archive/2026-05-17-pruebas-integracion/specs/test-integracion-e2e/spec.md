## ADDED Requirements

### Requirement: Infraestructura de integración con SQLite en memoria
El sistema SHALL disponer de fixtures pytest que levanten la app FastAPI con una base de datos SQLite en memoria, apliquen las migraciones/tablas al inicio de la sesión de test, y aseguren aislamiento por test mediante rollback de transacción.

#### Scenario: la base de datos se inicializa al comienzo de la sesión de integración
- **WHEN** comienza la sesión de pytest con `@pytest.mark.integration`
- **THEN** se crean todas las tablas SQLModel sobre `sqlite:///:memory:` y se cargan los datos seed (Roles, EstadoPedidos)

#### Scenario: cada test recibe una sesión aislada
- **WHEN** dos tests de integración corren en secuencia
- **THEN** los datos escritos por el primer test no son visibles en el segundo

#### Scenario: el cliente HTTP es un httpx.AsyncClient con ASGITransport
- **WHEN** se usa el fixture `async_client` en un test de integración
- **THEN** el fixture provee un `httpx.AsyncClient` conectado a la app sin levantar servidor real

### Requirement: Flujo de integración — Autenticación
El sistema SHALL tener tests de integración que validen el flujo completo de autenticación: registro, login y acceso protegido.

#### Scenario: registro de nuevo usuario retorna 201
- **WHEN** se hace POST a `/api/v1/auth/register` con email y password válidos
- **THEN** se retorna HTTP 201 con el usuario creado y sin exponer el hash de contraseña

#### Scenario: login exitoso retorna access y refresh tokens
- **WHEN** se hace POST a `/api/v1/auth/login` con credenciales válidas
- **THEN** se retorna HTTP 200 con `access_token` y `refresh_token`

#### Scenario: endpoint protegido rechaza request sin token
- **WHEN** se hace GET a un endpoint que requiere autenticación sin Authorization header
- **THEN** se retorna HTTP 401

#### Scenario: endpoint protegido acepta request con token válido
- **WHEN** se hace GET a un endpoint protegido con Bearer token válido
- **THEN** se retorna HTTP 200

### Requirement: Flujo de integración — Catálogo de productos
El sistema SHALL tener tests de integración para el catálogo que validen la visibilidad pública y el CRUD autenticado.

#### Scenario: listar productos sin autenticación retorna lista vacía o productos
- **WHEN** se hace GET a `/api/v1/productos` sin token
- **THEN** se retorna HTTP 200 con una lista (puede estar vacía si no hay seed de productos)

#### Scenario: crear producto como ADMIN retorna 201
- **WHEN** un usuario ADMIN hace POST a `/api/v1/productos` con payload completo y válido
- **THEN** se retorna HTTP 201 y el producto aparece en GET `/api/v1/productos`

#### Scenario: crear producto como CLIENT retorna 403
- **WHEN** un usuario con rol CLIENT hace POST a `/api/v1/productos`
- **THEN** se retorna HTTP 403

### Requirement: Flujo de integración — Creación de pedido
El sistema SHALL tener tests de integración que validen la creación de un pedido completo desde el carrito.

#### Scenario: cliente crea pedido con productos disponibles
- **WHEN** un usuario autenticado con rol CLIENT hace POST a `/api/v1/pedidos` con ítems válidos
- **THEN** se retorna HTTP 201, el pedido queda en estado PENDIENTE y el stock de los productos disminuye

#### Scenario: cliente no puede crear pedido con producto sin stock
- **WHEN** un usuario CLIENT intenta crear un pedido con cantidad mayor al stock disponible
- **THEN** se retorna HTTP 422 o HTTP 400 con mensaje indicando stock insuficiente

#### Scenario: listar pedidos propios retorna solo los del cliente autenticado
- **WHEN** un usuario CLIENT hace GET a `/api/v1/pedidos`
- **THEN** se retorna HTTP 200 con solo los pedidos del cliente autenticado

### Requirement: Flujo de integración — Webhook de pago
El sistema SHALL tener tests de integración que validen el procesamiento del webhook de MercadoPago y la transición automática de estado.

#### Scenario: webhook con pago aprobado confirma el pedido
- **WHEN** se hace POST a `/api/v1/pagos/webhook` con payload de pago aprobado para un pedido PENDIENTE
- **THEN** el pedido transiciona a CONFIRMADO y el `HistorialEstadoPedido` registra la transición

#### Scenario: webhook duplicado es ignorado (idempotencia)
- **WHEN** se hace POST a `/api/v1/pagos/webhook` dos veces con el mismo `mp_payment_id`
- **THEN** la segunda llamada retorna HTTP 200 sin crear un segundo registro de pago ni duplicar la transición

#### Scenario: webhook con pago rechazado no modifica el estado del pedido
- **WHEN** se hace POST a `/api/v1/pagos/webhook` con status `rejected`
- **THEN** el pedido permanece en PENDIENTE

### Requirement: Flujo de integración — Transición de estados de pedido
El sistema SHALL tener tests de integración que validen la máquina de estados del pedido según los roles autorizados.

#### Scenario: PEDIDOS puede avanzar pedido de CONFIRMADO a EN_PREP
- **WHEN** un usuario con rol PEDIDOS hace PATCH a `/api/v1/pedidos/{id}/estado` con `{ "nuevo_estado": "EN_PREP" }`
- **THEN** se retorna HTTP 200 y el pedido queda en EN_PREP

#### Scenario: CLIENT no puede avanzar el estado de un pedido
- **WHEN** un usuario CLIENT hace PATCH a `/api/v1/pedidos/{id}/estado`
- **THEN** se retorna HTTP 403

#### Scenario: cancelar pedido CONFIRMADO restaura el stock
- **WHEN** un usuario ADMIN cancela un pedido en estado CONFIRMADO
- **THEN** el pedido queda CANCELADO y el stock de los productos del detalle se restaura a los valores previos

#### Scenario: no se puede cancelar un pedido ENTREGADO
- **WHEN** se intenta cancelar un pedido en estado ENTREGADO
- **THEN** se retorna HTTP 422 o HTTP 400 indicando transición inválida
