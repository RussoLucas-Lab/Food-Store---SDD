# Tasks: Administración General

## 1. Backend — Modelo y migración

- [x] 1.1 Verificar si el campo `activo` existe en el modelo `Usuario` (`backend/modules/clientes/model.py`); si falta, agregarlo como `bool` not null con default `true`
- [x] 1.2 Crear migración Alembic para el campo `activo` en `Usuario` (default `true`, not null) y aplicarla con `alembic upgrade head`
- [x] 1.3 Actualizar el seed (`app/db/seed.py`) para que el usuario admin se cree con `activo=true`

## 2. Backend — Módulo admin: estructura y métricas

- [x] 2.1 Crear la estructura del módulo `backend/modules/admin/` con `__init__.py`, `router.py`, `service.py`, `repository.py`, `schemas.py`
- [x] 2.2 Definir schemas Pydantic de métricas en `admin/schemas.py`: `ResumenMetricasRead`, `PuntoVentaRead`, `ProductoTopRead`, `PedidoPorEstadoRead`, y los schemas de query (`granularidad` enum dia/semana/mes, validación de rango `desde`/`hasta`)
- [x] 2.3 Implementar en `admin/repository.py` la query de resumen: `SUM(total)` de pedidos en estados de venta efectiva (CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO), `COUNT` de pedidos, `COUNT` de usuarios y `COUNT` de productos con `stock=0`
- [x] 2.4 Implementar en `admin/repository.py` la query de serie temporal de ventas con `DATE_TRUNC` según granularidad, filtrada por `desde`/`hasta` y por estados de venta efectiva
- [x] 2.5 Implementar en `admin/repository.py` la query de top de productos: `GROUP BY` producto sobre `DetallePedido.cantidad` de pedidos efectivos, ordenado desc, limitado por `top`
- [x] 2.6 Implementar en `admin/repository.py` la query de distribución de pedidos por estado: `COUNT GROUP BY estado` con filtro opcional `desde`/`hasta`
- [x] 2.7 Implementar `AdminMetricasService` en `admin/service.py` orquestando las queries vía UoW, validando el rango de fechas invertido (lanza HTTP 422)
- [x] 2.8 Implementar en `admin/router.py` los 4 endpoints de métricas (`GET /api/v1/admin/metricas/resumen`, `/ventas`, `/productos-top`, `/pedidos-por-estado`) con `require_roles("ADMIN")`

## 3. Backend — Gestión de usuarios

- [x] 3.1 Definir schemas de gestión de usuarios en `admin/schemas.py`: `UsuarioAdminRead` (datos + roles + `activo`, sin hash de contraseña), `UsuarioUpdate` (datos y roles), `UsuarioActivoUpdate`, y schema de query de listado (`page`, `size`, `q`, `rol`, `activo`)
- [x] 3.2 Verificar/extender el repositorio de `clientes` para soportar listado de usuarios con búsqueda por nombre/email, filtros por rol y `activo`, y paginación; agregar métodos faltantes
- [x] 3.3 Implementar `AdminUsuariosService` en `admin/service.py` orquestando vía UoW el repo de `clientes`, el catálogo de roles y la revocación de refresh tokens
- [x] 3.4 Implementar en el service el listado de usuarios paginado con búsqueda y filtros, garantizando que la respuesta nunca exponga hashes de contraseña
- [x] 3.5 Implementar en el service la edición de datos y roles: validar que los roles existen en el catálogo (HTTP 422), validar RN-RB04 (no dejar al sistema sin ADMIN → HTTP 409), revocar refresh tokens del usuario en la misma transacción cuando cambian los roles, devolver HTTP 404 si el usuario no existe
- [x] 3.6 Implementar en el service la activación/desactivación de cuenta: modificar `activo`, revocar refresh tokens al desactivar, rechazar auto-desactivación (HTTP 409), rechazar desactivar al último ADMIN activo (HTTP 409)
- [x] 3.7 Implementar en `admin/router.py` los endpoints de usuarios (`GET /api/v1/admin/usuarios`, `PATCH/PUT /api/v1/admin/usuarios/{id}` para datos+roles y para `activo`) con `require_roles("ADMIN")`
- [x] 3.8 Registrar el router de `admin` en `backend/main.py` bajo el prefijo `/api/v1/admin`

## 4. Backend — Login y RBAC ampliado

- [x] 4.1 Modificar el flujo de login en `auth` para rechazar con HTTP 403 a usuarios con `activo=false`, sin emitir access ni refresh token
- [x] 4.2 Ajustar `require_roles` en los routers de catálogo (categorías, ingredientes, productos) para aceptar `("ADMIN", "STOCK")`
- [x] 4.3 Ajustar `require_roles` en los routers de pedidos/despacho para aceptar `("ADMIN", "PEDIDOS")`

## 5. Backend — Tests

- [x] 5.1 Tests unitarios de `AdminMetricasService`: resumen excluye pedidos PENDIENTE/CANCELADO, serie temporal por granularidad, top de productos ordenado, distribución por estado, rango de fechas invertido lanza error
- [x] 5.2 Tests unitarios de `AdminUsuariosService`: listado con búsqueda/filtros, edición de roles revoca tokens, rol inexistente rechazado, RN-RB04 rechaza dejar sin ADMIN, auto-desactivación rechazada
- [x] 5.3 Tests de integración de los endpoints de métricas: HTTP 200 con datos, HTTP 422 granularidad/rango inválido, HTTP 403 para no-ADMIN, HTTP 401 sin token
- [x] 5.4 Tests de integración de los endpoints de usuarios: listado paginado sin contraseñas, edición de datos/roles, activación/desactivación, HTTP 403 para no-ADMIN, HTTP 404 usuario inexistente
- [x] 5.5 Tests de integración del login: cuenta desactivada → HTTP 403, cuenta activa → HTTP 200, cuenta reactivada → HTTP 200; y del RBAC ampliado (ADMIN accede a catálogo y a pedidos)

## 6. Frontend — Servicios y hooks

- [x] 6.1 Implementar `adminMetricasApi` en `features/admin/services/` con las funciones que consumen los 4 endpoints de métricas
- [x] 6.2 Implementar `adminUsuariosApi` en `features/admin/services/` con las funciones de listado, edición de datos/roles y toggle de `activo`
- [x] 6.3 Implementar los hooks de métricas con TanStack Query: `useMetricasResumen`, `useMetricasVentas`, `useMetricasProductosTop`, `useMetricasPedidosEstado`
- [x] 6.4 Implementar los hooks de usuarios con TanStack Query: `useUsuarios` (query) y `useUpdateUsuario`, `useToggleUsuarioActivo` (mutations que invalidan la query de listado)

## 7. Frontend — Layout y navegación del panel

- [x] 7.1 Implementar el componente `AdminNav` que muestra los enlaces de navegación filtrados según el rol del usuario autenticado (ADMIN: todo; STOCK: Catálogo/Stock; PEDIDOS: Despacho)
- [x] 7.2 Implementar la página `AdminLayout` que compone `AdminNav` y el área de contenido del panel
- [x] 7.3 Registrar las rutas del panel de administración en `frontend/src/router.tsx` protegidas con el guard de rutas por rol existente

## 8. Frontend — Dashboard de métricas

- [x] 8.1 Verificar/instalar `recharts` como dependencia del frontend
- [x] 8.2 Implementar el componente `KpiCard` para mostrar un KPI individual
- [x] 8.3 Implementar `VentasLineChart` (LineChart de recharts) con selector de rango de fechas y granularidad, consumiendo `useMetricasVentas`
- [x] 8.4 Implementar `TopProductosBarChart` (BarChart de recharts) con filtro de fecha, consumiendo `useMetricasProductosTop`
- [x] 8.5 Implementar `PedidosEstadoPieChart` (PieChart de recharts) con filtro de fecha, consumiendo `useMetricasPedidosEstado`
- [x] 8.6 Implementar la página `DashboardPage` que compone las `KpiCard` (con `useMetricasResumen`) y los tres gráficos, cada uno con sus propios estados de carga y error independientes

## 9. Frontend — Gestión de usuarios

- [x] 9.1 Implementar el componente `UsuarioRolEditor` para seleccionar/editar el conjunto de roles de un usuario
- [x] 9.2 Implementar el componente `UsuarioRow` con los datos del usuario, el `UsuarioRolEditor` y el control de activar/desactivar cuenta
- [x] 9.3 Implementar la página `UsuariosPage` con búsqueda, filtros (rol, activo) y paginación, consumiendo `useUsuarios`, mostrando errores de mutación sin alterar el listado

## 10. Frontend — Catálogo, stock y despacho

- [x] 10.1 Implementar la página `CatalogoAdminPage` para gestión de categorías, ingredientes y productos consumiendo los endpoints CRUD de catálogo existentes (crear, editar, eliminar)
- [x] 10.2 Implementar el componente `StockAlertList` que marca como bajo stock los productos con `stock` por debajo de un umbral configurable en el cliente (default 5)
- [x] 10.3 Implementar la página `StockPage` que lista productos (incluidos no disponibles), muestra `StockAlertList` con umbral configurable, y permite actualizar stock vía `PATCH /api/v1/productos/{id}/stock`
- [x] 10.4 Integrar la vista de despacho de pedidos existente como sección Despacho dentro del panel de administración (ADMIN y PEDIDOS)

## 11. Frontend — Tests

- [x] 11.1 Test de `AdminNav`: renderiza la navegación correcta según el rol (ADMIN, STOCK, PEDIDOS)
- [x] 11.2 Test de `DashboardPage`: estados de carga y error independientes por gráfico
- [x] 11.3 Test de `UsuariosPage`/`UsuarioRow`: búsqueda filtra el listado, mutación de rol y de estado invalidan la query, error de mutación se muestra sin actualizar el listado
- [x] 11.4 Test de `StockAlertList`: recalcula las alertas al cambiar el umbral configurable

## 12. Verificación final

- [x] 12.1 Ejecutar la suite de tests del backend (`pytest`) y del frontend; confirmar que pasan
- [x] 12.2 Verificar manualmente el flujo end-to-end: login ADMIN, dashboard con gráficos, gestión de usuarios (cambio de rol revoca tokens), gestión de catálogo/stock, acceso por rol STOCK y PEDIDOS
- [x] 12.3 Confirmar que ningún `Service` llama `session.commit()` directo (todo vía UoW) y que las respuestas nunca exponen hashes de contraseña
