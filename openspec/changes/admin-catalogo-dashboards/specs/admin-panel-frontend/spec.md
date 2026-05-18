## MODIFIED Requirements

### Requirement: Layout del panel de administración con navegación por rol
El sistema SHALL proveer un layout de administración (`AdminLayout`) que muestra una navegación filtrada según el rol del usuario autenticado. El rol ADMIN SHALL ver todas las secciones (Dashboard, Usuarios, Categorías, Ingredientes, Productos, Stock, Despacho); el rol STOCK SHALL ver solo Categorías, Ingredientes, Productos y Stock; el rol PEDIDOS SHALL ver solo Despacho. Las rutas del panel SHALL estar protegidas por el guard de rutas por rol existente, de modo que un usuario sin un rol de gestión no pueda acceder.

#### Scenario: ADMIN ve la navegación completa con los nuevos dashboards de catálogo
- **WHEN** un usuario con rol ADMIN entra al panel de administración
- **THEN** la navegación muestra Dashboard, Usuarios, Categorías, Ingredientes, Productos, Stock y Despacho

#### Scenario: STOCK ve navegación con los tres dashboards de catálogo
- **WHEN** un usuario con rol STOCK entra al panel
- **THEN** la navegación muestra Categorías, Ingredientes, Productos y Stock, sin Dashboard ni Usuarios

#### Scenario: PEDIDOS ve solo Despacho
- **WHEN** un usuario con rol PEDIDOS entra al panel
- **THEN** la navegación muestra solo Despacho

#### Scenario: Cliente sin rol de gestión es bloqueado
- **WHEN** un usuario con rol CLIENT intenta navegar a una ruta del panel de administración
- **THEN** el guard de rutas impide el acceso y lo redirige fuera del panel

#### Scenario: Redirect de ruta obsoleta /admin/catalogo
- **WHEN** un usuario navega a la ruta antigua `/admin/catalogo`
- **THEN** el sistema lo redirige automáticamente a `/admin/categorias`
