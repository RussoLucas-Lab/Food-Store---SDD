## ADDED Requirements

### Requirement: Layout del panel de administración con navegación por rol
El sistema SHALL proveer un layout de administración (`AdminLayout`) que muestra una navegación filtrada según el rol del usuario autenticado. El rol ADMIN SHALL ver todas las secciones (Dashboard, Usuarios, Catálogo, Stock, Despacho); el rol STOCK SHALL ver solo Catálogo y Stock; el rol PEDIDOS SHALL ver solo Despacho. Las rutas del panel SHALL estar protegidas por el guard de rutas por rol existente, de modo que un usuario sin un rol de gestión no pueda acceder.

#### Scenario: ADMIN ve la navegación completa
- **WHEN** un usuario con rol ADMIN entra al panel de administración
- **THEN** la navegación muestra Dashboard, Usuarios, Catálogo, Stock y Despacho

#### Scenario: STOCK ve navegación restringida
- **WHEN** un usuario con rol STOCK entra al panel
- **THEN** la navegación muestra solo Catálogo y Stock, sin Dashboard ni Usuarios

#### Scenario: PEDIDOS ve solo Despacho
- **WHEN** un usuario con rol PEDIDOS entra al panel
- **THEN** la navegación muestra solo Despacho

#### Scenario: Cliente sin rol de gestión es bloqueado
- **WHEN** un usuario con rol CLIENT intenta navegar a una ruta del panel de administración
- **THEN** el guard de rutas impide el acceso y lo redirige fuera del panel

### Requirement: Dashboard de métricas con gráficos
El sistema SHALL proveer una pantalla de Dashboard, accesible solo para rol ADMIN, que muestra los KPIs del negocio en tarjetas (`KpiCard`) y tres gráficos recharts: una serie temporal de ventas (LineChart), un ranking de productos más vendidos (BarChart) y la distribución de pedidos por estado (PieChart). Cada gráfico SHALL obtener sus datos del endpoint de métricas correspondiente mediante un hook de TanStack Query independiente, y SHALL cargarse de forma independiente con sus propios estados de carga y error.

#### Scenario: ADMIN visualiza el dashboard
- **WHEN** un ADMIN abre la pantalla de Dashboard
- **THEN** se muestran las tarjetas de KPIs y los tres gráficos con los datos de las métricas

#### Scenario: Estados de carga independientes
- **WHEN** uno de los endpoints de métricas aún no respondió
- **THEN** ese gráfico muestra su propio indicador de carga sin bloquear el resto del dashboard

#### Scenario: Error al cargar una métrica
- **WHEN** un endpoint de métricas devuelve un error
- **THEN** el gráfico correspondiente muestra un mensaje de error sin romper el resto del dashboard

#### Scenario: Filtro de fecha por gráfico
- **WHEN** el ADMIN cambia el rango de fechas de un gráfico
- **THEN** ese gráfico recarga sus datos con el nuevo filtro sin afectar a los demás

### Requirement: Pantalla de gestión de usuarios
El sistema SHALL proveer una pantalla de gestión de usuarios, accesible solo para rol ADMIN, que lista los usuarios con búsqueda, filtros y paginación consumiendo el endpoint de listado. Cada fila (`UsuarioRow`) SHALL permitir editar los roles del usuario mediante `UsuarioRolEditor` y activar o desactivar la cuenta. Las mutaciones SHALL invalidar la query de listado para refrescar la UI tras un cambio exitoso.

#### Scenario: ADMIN lista y busca usuarios
- **WHEN** un ADMIN abre la pantalla de usuarios y escribe un término de búsqueda
- **THEN** el listado se filtra mostrando solo los usuarios coincidentes

#### Scenario: ADMIN cambia el rol de un usuario
- **WHEN** un ADMIN modifica los roles de un usuario y confirma
- **THEN** la mutación se envía al backend y, al tener éxito, el listado se refresca con los roles actualizados

#### Scenario: ADMIN activa o desactiva una cuenta
- **WHEN** un ADMIN cambia el estado activo de un usuario
- **THEN** la mutación se envía al backend y el listado se refresca con el nuevo estado

#### Scenario: Error de mutación
- **WHEN** una mutación de usuario falla (por ejemplo, dejaría al sistema sin ADMIN)
- **THEN** la pantalla muestra el mensaje de error y no actualiza el listado

### Requirement: Panel de gestión de catálogo
El sistema SHALL proveer pantallas de gestión de catálogo (categorías, ingredientes y productos), accesibles para los roles ADMIN y STOCK, que consumen los endpoints CRUD de catálogo ya existentes. Las pantallas SHALL permitir crear, editar y eliminar entidades del catálogo según los permisos del backend.

#### Scenario: STOCK gestiona el catálogo
- **WHEN** un usuario con rol STOCK abre la pantalla de gestión de catálogo
- **THEN** puede crear, editar y eliminar categorías, ingredientes y productos

#### Scenario: ADMIN gestiona el catálogo
- **WHEN** un usuario con rol ADMIN abre la pantalla de gestión de catálogo
- **THEN** tiene el mismo acceso de gestión que el rol STOCK

#### Scenario: Operación rechazada por el backend
- **WHEN** una operación de catálogo es rechazada por el backend
- **THEN** la pantalla muestra el error devuelto sin alterar el estado local

### Requirement: Pantalla de stock con alertas de bajo stock
El sistema SHALL proveer una pantalla de Stock, accesible para los roles ADMIN y STOCK, que lista los productos (incluyendo los no disponibles) consumiendo el endpoint de listado de productos. La pantalla SHALL marcar como "bajo stock" los productos cuyo `stock` esté por debajo de un umbral configurable en el cliente con valor por defecto 5, y SHALL permitir actualizar el stock de un producto mediante el endpoint `PATCH /api/v1/productos/{id}/stock` existente.

#### Scenario: Productos con bajo stock se destacan
- **WHEN** un usuario con rol STOCK o ADMIN abre la pantalla de Stock
- **THEN** los productos con `stock` menor al umbral (default 5) se muestran marcados como bajo stock en `StockAlertList`

#### Scenario: Actualización de stock
- **WHEN** un usuario actualiza el stock de un producto
- **THEN** la mutación llama a `PATCH /api/v1/productos/{id}/stock` y, al tener éxito, el listado refleja el nuevo stock

#### Scenario: Umbral configurable
- **WHEN** el usuario cambia el umbral de bajo stock en el cliente
- **THEN** la lista de alertas se recalcula según el nuevo umbral sin recargar del servidor

### Requirement: Integración de la vista de despacho de pedidos
El sistema SHALL integrar la vista de despacho de pedidos ya existente dentro del panel de administración, accesible para los roles ADMIN y PEDIDOS desde la navegación del panel.

#### Scenario: PEDIDOS accede al despacho desde el panel
- **WHEN** un usuario con rol PEDIDOS abre la sección Despacho del panel
- **THEN** se muestra la vista de despacho de pedidos existente

#### Scenario: ADMIN accede al despacho desde el panel
- **WHEN** un usuario con rol ADMIN abre la sección Despacho del panel
- **THEN** se muestra la vista de despacho de pedidos existente
