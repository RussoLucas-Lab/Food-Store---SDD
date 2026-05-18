## ADDED Requirements

### Requirement: Crear dirección de entrega

El sistema SHALL permitir a un cliente autenticado crear una dirección de entrega asociada a su `user_id`. La dirección DEBE incluir como mínimo calle, número, ciudad, provincia y código postal. El sistema SHALL asociar la dirección al cliente que realiza la petición, ignorando cualquier `cliente_id` o `user_id` recibido en el body.

#### Scenario: Cliente crea su primera dirección

- **WHEN** un cliente autenticado envía `POST /api/v1/clientes/me/direcciones` con calle, número, ciudad, provincia y código postal válidos
- **THEN** el sistema crea la dirección, la asocia a su `user_id`, devuelve HTTP 201 con la dirección creada incluyendo su `id`

#### Scenario: Crear dirección sin campos obligatorios

- **WHEN** un cliente autenticado envía `POST /api/v1/clientes/me/direcciones` sin calle o sin ciudad
- **THEN** el sistema rechaza la petición con HTTP 422 y no crea ninguna dirección

#### Scenario: Crear dirección sin autenticación

- **WHEN** una petición `POST /api/v1/clientes/me/direcciones` se envía sin token JWT válido
- **THEN** el sistema responde HTTP 401 y no crea ninguna dirección

### Requirement: Listar direcciones propias

El sistema SHALL permitir a un cliente autenticado listar únicamente sus propias direcciones de entrega no eliminadas. El sistema SHALL NOT incluir direcciones de otros clientes ni direcciones con soft delete aplicado.

#### Scenario: Cliente lista sus direcciones

- **WHEN** un cliente autenticado envía `GET /api/v1/clientes/me/direcciones`
- **THEN** el sistema devuelve HTTP 200 con la lista de sus direcciones activas, indicando cuál es la predeterminada

#### Scenario: Cliente sin direcciones

- **WHEN** un cliente autenticado sin direcciones registradas envía `GET /api/v1/clientes/me/direcciones`
- **THEN** el sistema devuelve HTTP 200 con una lista vacía

### Requirement: Editar dirección propia

El sistema SHALL permitir a un cliente autenticado modificar los campos de una dirección de entrega que le pertenece. El sistema SHALL rechazar la edición de direcciones que pertenecen a otro cliente.

#### Scenario: Cliente edita su dirección

- **WHEN** un cliente autenticado envía `PUT /api/v1/clientes/me/direcciones/{id}` sobre una dirección propia con datos válidos
- **THEN** el sistema actualiza la dirección y devuelve HTTP 200 con la dirección modificada

#### Scenario: Cliente intenta editar dirección ajena

- **WHEN** un cliente autenticado envía `PUT /api/v1/clientes/me/direcciones/{id}` sobre una dirección que pertenece a otro cliente
- **THEN** el sistema responde HTTP 403 y no modifica la dirección

#### Scenario: Editar dirección inexistente

- **WHEN** un cliente autenticado envía `PUT /api/v1/clientes/me/direcciones/{id}` con un `id` que no existe
- **THEN** el sistema responde HTTP 404

### Requirement: Eliminar dirección propia

El sistema SHALL permitir a un cliente autenticado eliminar una dirección de entrega propia mediante soft delete. El sistema SHALL rechazar la eliminación de direcciones de otro cliente.

#### Scenario: Cliente elimina su dirección

- **WHEN** un cliente autenticado envía `DELETE /api/v1/clientes/me/direcciones/{id}` sobre una dirección propia
- **THEN** el sistema marca la dirección como eliminada (soft delete), devuelve HTTP 204 y la dirección deja de aparecer en el listado

#### Scenario: Cliente intenta eliminar dirección ajena

- **WHEN** un cliente autenticado envía `DELETE /api/v1/clientes/me/direcciones/{id}` sobre una dirección de otro cliente
- **THEN** el sistema responde HTTP 403 y no elimina la dirección

### Requirement: Ownership de direcciones por usuario

El sistema SHALL garantizar que un cliente solo pueda ver, editar o eliminar direcciones cuyo `cliente_id` coincide con el `user_id` extraído de su token JWT. La verificación de propiedad SHALL realizarse en la capa de servicio, no confiar en datos enviados por el cliente.

#### Scenario: Acceso a dirección propia

- **WHEN** un cliente autenticado accede a una dirección cuyo `cliente_id` coincide con su `user_id`
- **THEN** el sistema permite la operación

#### Scenario: Acceso a dirección de otro usuario

- **WHEN** un cliente autenticado intenta acceder a una dirección cuyo `cliente_id` no coincide con su `user_id`
- **THEN** el sistema responde HTTP 403 sin revelar datos de la dirección
