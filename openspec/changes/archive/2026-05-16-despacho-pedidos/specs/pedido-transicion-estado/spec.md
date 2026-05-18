## ADDED Requirements

### Requirement: Avance de estado del pedido por la FSM

El sistema SHALL exponer el endpoint `PATCH /api/v1/pedidos/{id}/estado` que permite cambiar el estado de un pedido únicamente a través de transiciones válidas de la máquina de estados: PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO, más las cancelaciones definidas. El sistema MUST rechazar cualquier transición que no esté en el mapa de transiciones permitidas.

#### Scenario: Avance válido de CONFIRMADO a EN_PREPARACION

- **WHEN** un usuario con rol PEDIDOS o ADMIN solicita cambiar un pedido en estado CONFIRMADO al estado EN_PREPARACION
- **THEN** el sistema actualiza el estado del pedido a EN_PREPARACION, registra la transición en el historial y responde HTTP 200 con el pedido actualizado

#### Scenario: Avance válido de EN_PREPARACION a EN_CAMINO

- **WHEN** un usuario con rol PEDIDOS o ADMIN solicita cambiar un pedido en estado EN_PREPARACION al estado EN_CAMINO
- **THEN** el sistema actualiza el estado a EN_CAMINO, registra la transición en el historial y responde HTTP 200

#### Scenario: Avance válido de EN_CAMINO a ENTREGADO

- **WHEN** un usuario con rol PEDIDOS o ADMIN solicita cambiar un pedido en estado EN_CAMINO al estado ENTREGADO
- **THEN** el sistema actualiza el estado a ENTREGADO, registra la transición en el historial y responde HTTP 200

#### Scenario: Transición con salto de estado rechazada

- **WHEN** un usuario solicita cambiar un pedido en estado CONFIRMADO directamente al estado EN_CAMINO
- **THEN** el sistema rechaza la solicitud con HTTP 409 y no modifica el estado del pedido

#### Scenario: Retroceso de estado rechazado

- **WHEN** un usuario solicita cambiar un pedido en estado EN_CAMINO al estado EN_PREPARACION
- **THEN** el sistema rechaza la solicitud con HTTP 409 y no modifica el estado del pedido

### Requirement: Estados terminales sin transiciones

El sistema SHALL tratar los estados ENTREGADO y CANCELADO como terminales: ninguna transición adicional MUST ser permitida desde estos estados.

#### Scenario: Transición desde estado ENTREGADO rechazada

- **WHEN** un usuario solicita cambiar el estado de un pedido que ya está ENTREGADO
- **THEN** el sistema rechaza la solicitud con HTTP 409 y no modifica el pedido

#### Scenario: Transición desde estado CANCELADO rechazada

- **WHEN** un usuario solicita cambiar el estado de un pedido que ya está CANCELADO
- **THEN** el sistema rechaza la solicitud con HTTP 409 y no modifica el pedido

### Requirement: Transición PENDIENTE a CONFIRMADO solo automática

El sistema MUST NOT permitir la transición manual PENDIENTE → CONFIRMADO a través del endpoint de cambio de estado. Esa transición solo ocurre de forma automática por la confirmación de pago de MercadoPago.

#### Scenario: Confirmación manual de pedido rechazada

- **WHEN** cualquier usuario, incluido un ADMIN, solicita cambiar un pedido en estado PENDIENTE al estado CONFIRMADO mediante el endpoint de cambio de estado
- **THEN** el sistema rechaza la solicitud con HTTP 409 y el pedido permanece en PENDIENTE

### Requirement: Autorización por rol para cada transición

El sistema SHALL validar que el rol del usuario autenticado esté autorizado para la transición solicitada. Las transiciones de preparación, envío y entrega SHALL estar permitidas a PEDIDOS y ADMIN. La cancelación desde EN_PREPARACION SHALL estar permitida únicamente a ADMIN. La cancelación desde CONFIRMADO SHALL estar permitida a PEDIDOS y ADMIN. La cancelación desde PENDIENTE SHALL estar permitida al cliente propietario, a PEDIDOS y a ADMIN.

#### Scenario: Cliente intenta avanzar un pedido

- **WHEN** un usuario con rol CLIENT solicita cambiar un pedido en estado CONFIRMADO al estado EN_PREPARACION
- **THEN** el sistema rechaza la solicitud con HTTP 403 y no modifica el pedido

#### Scenario: Rol PEDIDOS intenta cancelar desde EN_PREPARACION

- **WHEN** un usuario con rol PEDIDOS solicita cancelar un pedido que está en estado EN_PREPARACION
- **THEN** el sistema rechaza la solicitud con HTTP 403 y el pedido permanece en EN_PREPARACION

#### Scenario: ADMIN cancela desde EN_PREPARACION

- **WHEN** un usuario con rol ADMIN solicita cancelar un pedido en estado EN_PREPARACION con un motivo
- **THEN** el sistema cambia el estado a CANCELADO, restaura el stock y responde HTTP 200

#### Scenario: Cliente cancela su propio pedido pendiente

- **WHEN** un usuario con rol CLIENT solicita cancelar un pedido en estado PENDIENTE del cual es propietario, indicando un motivo
- **THEN** el sistema cambia el estado a CANCELADO y responde HTTP 200

#### Scenario: Cliente intenta cancelar un pedido ajeno

- **WHEN** un usuario con rol CLIENT solicita cancelar un pedido en estado PENDIENTE que pertenece a otro cliente
- **THEN** el sistema rechaza la solicitud con HTTP 403 y no modifica el pedido

### Requirement: Motivo obligatorio al cancelar

El sistema MUST exigir un motivo no vacío cuando la transición solicitada lleva al estado CANCELADO.

#### Scenario: Cancelación sin motivo rechazada

- **WHEN** un usuario solicita cancelar un pedido sin proporcionar un motivo o con un motivo vacío
- **THEN** el sistema rechaza la solicitud con HTTP 422 y no modifica el pedido

#### Scenario: Cancelación con motivo aceptada

- **WHEN** un usuario autorizado solicita cancelar un pedido proporcionando un motivo no vacío
- **THEN** el sistema cambia el estado a CANCELADO y guarda el motivo en el historial

### Requirement: Restauración atómica de stock al cancelar

El sistema SHALL restaurar el stock de todos los productos del pedido cuando se cancela un pedido cuyo estado de origen es CONFIRMADO o EN_PREPARACION, en la misma operación transaccional que actualiza el estado y registra el historial. El sistema MUST NOT restaurar stock cuando el estado de origen es PENDIENTE.

#### Scenario: Cancelación de pedido confirmado restaura stock

- **WHEN** un usuario autorizado cancela un pedido en estado CONFIRMADO
- **THEN** el sistema incrementa el stock de cada producto del pedido en la cantidad correspondiente y persiste el cambio junto con el nuevo estado

#### Scenario: Cancelación de pedido pendiente no altera stock

- **WHEN** un usuario autorizado cancela un pedido en estado PENDIENTE
- **THEN** el sistema cambia el estado a CANCELADO sin modificar el stock de ningún producto

### Requirement: Registro append-only de cada transición

El sistema MUST registrar cada transición de estado exitosa como un nuevo registro en el historial del pedido, conservando el estado anterior, el estado nuevo, el usuario que la ejecutó y una observación. El sistema MUST NOT actualizar ni eliminar registros de historial existentes.

#### Scenario: Transición genera registro de historial

- **WHEN** una transición de estado se completa con éxito
- **THEN** el sistema inserta un nuevo registro de historial con el estado anterior, el estado nuevo, el identificador del usuario y la observación, sin modificar registros previos

#### Scenario: Pedido inexistente

- **WHEN** un usuario solicita cambiar el estado de un pedido que no existe
- **THEN** el sistema responde HTTP 404 y no registra ningún historial
