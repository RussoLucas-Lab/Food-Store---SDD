## ADDED Requirements

### Requirement: Resumen general de métricas
El sistema SHALL exponer `GET /api/v1/admin/metricas/resumen`, accesible solo para usuarios con rol ADMIN, que devuelve los KPIs del negocio: ventas totales, cantidad de pedidos, cantidad de usuarios registrados y cantidad de productos sin stock. Las "ventas" se calculan sobre pedidos en estados de venta efectiva (CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO), usando el campo `total` snapshot del pedido, y excluyen los estados PENDIENTE y CANCELADO.

#### Scenario: ADMIN consulta el resumen
- **WHEN** un usuario autenticado con rol ADMIN hace `GET /api/v1/admin/metricas/resumen`
- **THEN** el sistema responde HTTP 200 con `ventas_totales`, `cantidad_pedidos`, `cantidad_usuarios` y `productos_sin_stock`

#### Scenario: Las ventas excluyen pedidos no efectivos
- **WHEN** existen pedidos en estado PENDIENTE o CANCELADO
- **THEN** el monto de `ventas_totales` no incluye el `total` de esos pedidos

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario con rol CLIENT, STOCK o PEDIDOS hace `GET /api/v1/admin/metricas/resumen`
- **THEN** el sistema responde HTTP 403 sin exponer los datos

#### Scenario: Petición sin autenticación
- **WHEN** se hace `GET /api/v1/admin/metricas/resumen` sin token de acceso válido
- **THEN** el sistema responde HTTP 401

### Requirement: Serie temporal de ventas
El sistema SHALL exponer `GET /api/v1/admin/metricas/ventas`, accesible solo para rol ADMIN, que devuelve una serie temporal del monto de ventas agrupado por período. Acepta los parámetros de query `desde` (fecha), `hasta` (fecha) y `granularidad` con valores `dia`, `semana` o `mes`. La agregación usa `DATE_TRUNC` según la granularidad y solo considera pedidos en estados de venta efectiva.

#### Scenario: ADMIN consulta ventas por día
- **WHEN** un ADMIN hace `GET /api/v1/admin/metricas/ventas?desde=2026-01-01&hasta=2026-01-31&granularidad=dia`
- **THEN** el sistema responde HTTP 200 con una lista de puntos `{periodo, monto}` ordenados cronológicamente, un punto por día del rango con ventas

#### Scenario: Granularidad inválida
- **WHEN** un ADMIN envía `granularidad` con un valor distinto de `dia`, `semana` o `mes`
- **THEN** el sistema responde HTTP 422 con un error de validación

#### Scenario: Rango de fechas invertido
- **WHEN** un ADMIN envía `desde` posterior a `hasta`
- **THEN** el sistema responde HTTP 422 con un error indicando que el rango es inválido

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario sin rol ADMIN hace `GET /api/v1/admin/metricas/ventas`
- **THEN** el sistema responde HTTP 403

### Requirement: Ranking de productos más vendidos
El sistema SHALL exponer `GET /api/v1/admin/metricas/productos-top`, accesible solo para rol ADMIN, que devuelve los productos más vendidos. Acepta los parámetros `top` (cantidad de resultados a devolver), `desde` y `hasta` (rango de fechas). El ranking agrega `DetallePedido.cantidad` de los pedidos en estados de venta efectiva y se ordena de mayor a menor cantidad vendida.

#### Scenario: ADMIN consulta el top de productos
- **WHEN** un ADMIN hace `GET /api/v1/admin/metricas/productos-top?top=5&desde=2026-01-01&hasta=2026-01-31`
- **THEN** el sistema responde HTTP 200 con como máximo 5 productos, cada uno con `producto_id`, `nombre` y `cantidad_vendida`, ordenados de mayor a menor cantidad

#### Scenario: Sin ventas en el rango
- **WHEN** un ADMIN consulta un rango de fechas sin pedidos efectivos
- **THEN** el sistema responde HTTP 200 con una lista vacía

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario sin rol ADMIN hace `GET /api/v1/admin/metricas/productos-top`
- **THEN** el sistema responde HTTP 403

### Requirement: Distribución de pedidos por estado
El sistema SHALL exponer `GET /api/v1/admin/metricas/pedidos-por-estado`, accesible solo para rol ADMIN, que devuelve la cantidad de pedidos agrupados por estado. Acepta los parámetros opcionales `desde` y `hasta` para filtrar por fecha de creación del pedido.

#### Scenario: ADMIN consulta la distribución por estado
- **WHEN** un ADMIN hace `GET /api/v1/admin/metricas/pedidos-por-estado?desde=2026-01-01&hasta=2026-01-31`
- **THEN** el sistema responde HTTP 200 con una lista de `{estado, cantidad}` cubriendo los estados con al menos un pedido en el rango

#### Scenario: Consulta sin filtro de fechas
- **WHEN** un ADMIN hace `GET /api/v1/admin/metricas/pedidos-por-estado` sin parámetros
- **THEN** el sistema responde HTTP 200 con la distribución de todos los pedidos históricos

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario sin rol ADMIN hace `GET /api/v1/admin/metricas/pedidos-por-estado`
- **THEN** el sistema responde HTTP 403
