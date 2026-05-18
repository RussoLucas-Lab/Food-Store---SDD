### Requirement: Listado de pedidos para gestores

El sistema SHALL exponer el endpoint `GET /api/v1/pedidos/gestion` que devuelve todos los pedidos del sistema, accesible únicamente para usuarios con rol PEDIDOS o ADMIN. El resultado MUST estar paginado mediante los parámetros `skip` y `limit`.

#### Scenario: Gestor lista todos los pedidos

- **WHEN** un usuario con rol PEDIDOS o ADMIN solicita el listado de gestión de pedidos
- **THEN** el sistema responde HTTP 200 con la lista paginada de todos los pedidos, ordenada por fecha de creación descendente

#### Scenario: Cliente intenta acceder al listado de gestión

- **WHEN** un usuario con rol CLIENT solicita el listado de gestión de pedidos
- **THEN** el sistema rechaza la solicitud con HTTP 403

#### Scenario: Solicitud sin autenticación

- **WHEN** una solicitud al listado de gestión llega sin token de autenticación
- **THEN** el sistema responde HTTP 401

### Requirement: Filtrado de pedidos por estado y fecha

El sistema SHALL permitir filtrar el listado de gestión por estado del pedido y por un rango de fechas de creación, mediante parámetros de consulta opcionales.

#### Scenario: Filtrado por estado

- **WHEN** un gestor solicita el listado de gestión filtrando por el estado EN_PREPARACION
- **THEN** el sistema responde con únicamente los pedidos que se encuentran en estado EN_PREPARACION

#### Scenario: Filtrado por rango de fechas

- **WHEN** un gestor solicita el listado de gestión indicando una fecha desde y una fecha hasta
- **THEN** el sistema responde con únicamente los pedidos cuya fecha de creación está dentro del rango indicado

#### Scenario: Sin filtros aplicados

- **WHEN** un gestor solicita el listado de gestión sin parámetros de filtro
- **THEN** el sistema responde con todos los pedidos paginados sin restricción de estado ni fecha

#### Scenario: Filtro de fecha con formato inválido

- **WHEN** un gestor solicita el listado de gestión con un parámetro de fecha en formato inválido
- **THEN** el sistema responde HTTP 422 sin devolver resultados

### Requirement: Acceso al detalle de cualquier pedido por gestores

El sistema SHALL permitir que usuarios con rol PEDIDOS o ADMIN consulten el detalle completo de cualquier pedido mediante `GET /api/v1/pedidos/{id}`, sin la restricción de propiedad que aplica al rol CLIENT. El detalle MUST incluir las líneas del pedido y el historial de estados.

#### Scenario: Gestor consulta detalle de un pedido ajeno

- **WHEN** un usuario con rol PEDIDOS o ADMIN consulta el detalle de un pedido que pertenece a cualquier cliente
- **THEN** el sistema responde HTTP 200 con el pedido, sus líneas y su historial de estados

#### Scenario: Cliente consulta detalle de su propio pedido

- **WHEN** un usuario con rol CLIENT consulta el detalle de un pedido del cual es propietario
- **THEN** el sistema responde HTTP 200 con el detalle completo del pedido

#### Scenario: Cliente intenta consultar detalle de pedido ajeno

- **WHEN** un usuario con rol CLIENT consulta el detalle de un pedido que pertenece a otro cliente
- **THEN** el sistema rechaza la solicitud con HTTP 403

#### Scenario: Detalle de pedido inexistente

- **WHEN** un usuario solicita el detalle de un pedido que no existe
- **THEN** el sistema responde HTTP 404
