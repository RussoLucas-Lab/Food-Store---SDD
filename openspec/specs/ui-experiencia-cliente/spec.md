### Requirement: uiStore para estado de UI global
El sistema SHALL implementar un `uiStore` Zustand (no persistido) con los campos `cartOpen: boolean`, `sidebarOpen: boolean`, y `confirmModal: { open: boolean; message: string; onConfirm: () => void } | null`.

#### Scenario: Abrir y cerrar carrito
- **WHEN** se llama `uiStore.setCartOpen(true)`
- **THEN** `uiStore.cartOpen` pasa a `true` y el CartDrawer se renderiza como visible

#### Scenario: Estado inicial
- **WHEN** la aplicación carga por primera vez
- **THEN** `cartOpen`, `sidebarOpen` son `false` y `confirmModal` es `null`

### Requirement: Skeleton loaders en páginas de carga
El sistema SHALL mostrar skeleton loaders mientras se cargan datos de la API en la CatalogoPage y ProductoDetailPage.

#### Scenario: Carga de catálogo
- **WHEN** la query de productos está en estado `isLoading`
- **THEN** se muestran tarjetas skeleton en lugar de las tarjetas reales

#### Scenario: Carga de detalle
- **WHEN** la query del producto individual está en estado `isLoading`
- **THEN** se muestra un skeleton del layout de detalle

### Requirement: Estados vacíos con CTA
El sistema SHALL mostrar estados vacíos informativos con una acción cuando las listas no tienen datos.

#### Scenario: Estado vacío en catálogo
- **WHEN** la API devuelve lista de productos vacía
- **THEN** se muestra "No hay productos disponibles" con ícono y sin elementos de error

#### Scenario: Estado vacío en mis pedidos (sin pedidos aún)
- **WHEN** el cliente no tiene pedidos
- **THEN** se muestra "Todavía no hiciste ningún pedido" con CTA "Ver catálogo"

### Requirement: Feedback de acciones con Toast
El sistema SHALL mostrar notificaciones Toast para confirmar acciones del usuario (add-to-cart, errores de red).

#### Scenario: Producto agregado al carrito
- **WHEN** el usuario agrega un producto exitosamente
- **THEN** aparece un toast verde "Producto agregado al carrito" que desaparece en 3 segundos

#### Scenario: Error al cargar datos
- **WHEN** una query de TanStack Query retorna error
- **THEN** aparece un toast rojo con el mensaje de error de la API o "Error de conexión"

### Requirement: Responsive básico en páginas nuevas
Las páginas CatalogoPage, ProductoDetailPage y CartDrawer SHALL adaptarse a viewports móviles (< 640px).

#### Scenario: Catálogo en mobile
- **WHEN** el viewport es menor a 640px
- **THEN** la grilla de productos muestra 1 columna en lugar de 3

#### Scenario: CartDrawer en mobile
- **WHEN** el CartDrawer está abierto en mobile
- **THEN** ocupa el ancho completo de la pantalla (full-width)

#### Scenario: ProductoDetailPage en mobile
- **WHEN** el viewport es menor a 640px
- **THEN** el layout de detalle es de 1 columna (imagen arriba, controles abajo)
