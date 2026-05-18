## ADDED Requirements

### Requirement: Panel de gestión de pedidos para gestores

El frontend SHALL ofrecer una página de gestión de pedidos accesible únicamente a usuarios con rol PEDIDOS o ADMIN, que liste los pedidos con sus filtros y permita acceder al detalle de cada uno.

#### Scenario: Gestor visualiza el listado de pedidos

- **WHEN** un usuario autenticado con rol PEDIDOS o ADMIN navega a la página de gestión de pedidos
- **THEN** la aplicación muestra la lista de pedidos con su identificador, cliente, estado actual, total y fecha de creación

#### Scenario: Cliente intenta acceder al panel de gestión

- **WHEN** un usuario con rol CLIENT intenta navegar a la ruta del panel de gestión de pedidos
- **THEN** la aplicación impide el acceso y lo redirige fuera de la página de gestión

#### Scenario: Gestor filtra el listado

- **WHEN** un gestor selecciona un estado o un rango de fechas en los filtros de la página de gestión
- **THEN** la aplicación actualiza el listado mostrando solo los pedidos que cumplen los filtros

### Requirement: Acciones de transición de estado en el panel de gestión

El frontend SHALL mostrar, en el detalle de un pedido del panel de gestión, únicamente las acciones de transición de estado válidas para el estado actual del pedido y el rol del usuario. Al cancelar, la interfaz MUST solicitar un motivo obligatorio.

#### Scenario: Gestor avanza el estado de un pedido

- **WHEN** un gestor abre el detalle de un pedido en estado CONFIRMADO y confirma la acción de pasar a EN_PREPARACION
- **THEN** la aplicación envía la solicitud al backend y, al recibir éxito, actualiza el estado mostrado del pedido

#### Scenario: Acciones limitadas al estado actual

- **WHEN** un gestor visualiza el detalle de un pedido en estado ENTREGADO
- **THEN** la aplicación no muestra ninguna acción de transición de estado

#### Scenario: Cancelación solicita motivo

- **WHEN** un gestor inicia la cancelación de un pedido
- **THEN** la aplicación solicita un motivo y no envía la solicitud hasta que el motivo no esté vacío

#### Scenario: Error de transición mostrado al usuario

- **WHEN** el backend rechaza una transición de estado solicitada desde el panel
- **THEN** la aplicación muestra un mensaje de error y conserva el estado previo del pedido en pantalla

### Requirement: Vista de Mis Pedidos para el cliente

El frontend SHALL ofrecer una página "Mis Pedidos" accesible al usuario con rol CLIENT, que liste sus pedidos con el estado actual y permita ver el detalle y la línea de tiempo de cada uno.

#### Scenario: Cliente visualiza sus pedidos

- **WHEN** un usuario con rol CLIENT navega a la página "Mis Pedidos"
- **THEN** la aplicación muestra la lista de los pedidos del cliente con su estado actual, total y fecha

#### Scenario: Cliente visualiza la línea de tiempo de un pedido

- **WHEN** un cliente abre el detalle de uno de sus pedidos
- **THEN** la aplicación muestra la secuencia de estados por los que pasó el pedido con sus marcas de tiempo

#### Scenario: Cliente cancela un pedido pendiente

- **WHEN** un cliente abre un pedido propio en estado PENDIENTE y confirma la cancelación indicando un motivo
- **THEN** la aplicación envía la solicitud al backend y, al recibir éxito, refleja el pedido en estado CANCELADO

#### Scenario: Cliente no puede cancelar un pedido ya confirmado

- **WHEN** un cliente abre un pedido propio cuyo estado no es PENDIENTE
- **THEN** la aplicación no muestra la acción de cancelación
