## ADDED Requirements

### Requirement: Validar disponibilidad de stock
El sistema SHALL validar que hay suficiente stock disponible de un ingrediente antes de permitir cualquier operación que implique consumo. El stock disponible se calcula como `cantidad_stock - cantidad_reservada` (cantidad_reservada viene de carrito/pedidos). La cantidad a descontar no puede ser negativa ni mayor que stock disponible.

#### Scenario: Verificar disponibilidad con stock suficiente
- **WHEN** un endpoint de validación consulta `puede_descontar(ingrediente_id=1, cantidad=500)` donde cantidad_stock es 1000 y no hay reservas
- **THEN** el sistema devuelve `true` indicando que hay disponibilidad

#### Scenario: Verificar disponibilidad con stock insuficiente
- **WHEN** un endpoint de validación consulta `puede_descontar(ingrediente_id=1, cantidad=1500)` donde cantidad_stock es 1000
- **THEN** el sistema devuelve `false` indicando que NO hay disponibilidad

#### Scenario: Verificar disponibilidad con cantidad negativa (operación inválida)
- **WHEN** un endpoint consulta `puede_descontar(ingrediente_id=1, cantidad=-100)`
- **THEN** el sistema rechaza con 400 Bad Request indicando "cantidad no puede ser negativa"

#### Scenario: Verificar disponibilidad de ingrediente inactivo
- **WHEN** un endpoint consulta `puede_descontar(ingrediente_id=5, cantidad=100)` donde el ingrediente está inactivo
- **THEN** el sistema rechaza con 410 Gone indicando "Ingrediente ya no está disponible"

### Requirement: Detectar stock bajo
El sistema SHALL detectar cuando el stock de un ingrediente cae por debajo de la cantidad mínima configurada. Esta detección es informativa (no bloquea operaciones) y es usada por admin para reorden.

#### Scenario: Stock por encima de cantidad mínima
- **WHEN** un usuario obtiene detalles de ingrediente donde cantidad_stock=1000 y cantidad_minima=100
- **THEN** la respuesta incluye `alerta_stock_bajo: false`

#### Scenario: Stock por debajo de cantidad mínima
- **WHEN** un usuario obtiene detalles de ingrediente donde cantidad_stock=50 y cantidad_minima=100
- **THEN** la respuesta incluye `alerta_stock_bajo: true`

#### Scenario: Stock exactamente igual a cantidad mínima
- **WHEN** un usuario obtiene detalles de ingrediente donde cantidad_stock=100 y cantidad_minima=100
- **THEN** la respuesta incluye `alerta_stock_bajo: false` (igual al mínimo es aceptable)

### Requirement: Calcular stock disponible con reservas
El sistema SHALL calcular el stock disponible considerando reservas de carrito/pedidos pendientes. El stock mostrado al público debe restar cantidad_reservada para evitar overselling. En respuestas de listado, cada ingrediente incluye `stock_disponible` (cantidad que puede venderse ahora).

#### Scenario: Listar ingredientes sin reservas
- **WHEN** un usuario obtiene listado de ingredientes donde un ingrediente tiene cantidad_stock=1000 y cantidad_reservada=0
- **THEN** en la respuesta, ese ingrediente muestra `stock_disponible: 1000`

#### Scenario: Listar ingredientes con reservas
- **WHEN** un usuario obtiene listado de ingredientes donde un ingrediente tiene cantidad_stock=1000 y cantidad_reservada=300 (de carrito activos)
- **THEN** en la respuesta, ese ingrediente muestra `stock_disponible: 700`

#### Scenario: Stock disponible es cero (aunque exista stock_físico)
- **WHEN** un usuario obtiene listado de ingredientes donde cantidad_stock=100 pero cantidad_reservada=100 (todo reservado)
- **THEN** en la respuesta, ese ingrediente muestra `stock_disponible: 0`

### Requirement: Registrar cambios de stock (auditoría básica)
El sistema SHALL registrar automáticamente cambios de stock con timestamp. Cada actualización manual de stock por admin se registra con: id del admin, cantidad anterior, cantidad nueva, motivo (ej: "ajuste manual", "compra de proveedor").

#### Scenario: Admin actualiza stock manualmente
- **WHEN** un admin envía `PUT /ingredientes/1` cambiando cantidad_stock de 1000 a 1200
- **THEN** se registra en auditoría: admin_id, timestamp, cantidad_anterior=1000, cantidad_nueva=1200, motivo="ajuste manual"

#### Scenario: Consultar historial de stock
- **WHEN** un admin envía `GET /ingredientes/1/historial-stock`
- **THEN** el sistema devuelve array con últimos 20 cambios de stock (timestamp, admin_id, cantidad_anterior, cantidad_nueva, motivo)
