## ADDED Requirements

### Requirement: Catálogo de productos accesible públicamente
El sistema SHALL proveer una página `/productos` que liste todos los productos disponibles (`disponible=true`, no eliminados). La página SHALL ser accesible sin autenticación.

#### Scenario: Cliente navega al catálogo
- **WHEN** un usuario (autenticado o no) visita `/productos`
- **THEN** el sistema muestra una grilla de tarjetas de productos con nombre, imagen (o placeholder), precio y botón "Agregar"

#### Scenario: Catálogo vacío
- **WHEN** la API no devuelve productos
- **THEN** el sistema muestra un estado vacío con mensaje "No hay productos disponibles" y sin errores

### Requirement: Filtro de productos por categoría
El sistema SHALL permitir filtrar los productos por categoría usando los parámetros de query de la API.

#### Scenario: Filtro por categoría
- **WHEN** el usuario selecciona una categoría del selector
- **THEN** la grilla muestra solo los productos de esa categoría

#### Scenario: Limpiar filtro
- **WHEN** el usuario selecciona "Todas las categorías"
- **THEN** la grilla vuelve a mostrar todos los productos disponibles

### Requirement: Búsqueda de productos por nombre
El sistema SHALL ofrecer un campo de búsqueda que filtre productos por nombre.

#### Scenario: Búsqueda con resultados
- **WHEN** el usuario escribe en el campo de búsqueda
- **THEN** la grilla muestra solo los productos cuyo nombre contiene el texto ingresado (case-insensitive)

#### Scenario: Búsqueda sin resultados
- **WHEN** la búsqueda no devuelve productos
- **THEN** el sistema muestra estado vacío "No se encontraron productos para tu búsqueda"

### Requirement: Página de detalle de producto
El sistema SHALL proveer una página `/productos/:id` con el detalle completo del producto.

#### Scenario: Ver detalle de producto
- **WHEN** el usuario hace clic en una tarjeta de producto
- **THEN** el sistema navega a `/productos/:id` y muestra nombre, descripción, precio, stock disponible e ingredientes

#### Scenario: Producto no encontrado
- **WHEN** el ID del producto no existe en la API
- **THEN** el sistema muestra un mensaje de error y un link para volver al catálogo

### Requirement: Selección de ingredientes a excluir
En la página de detalle, el sistema SHALL permitir al usuario marcar ingredientes a excluir antes de agregar al carrito.

#### Scenario: Excluir ingrediente removible
- **WHEN** el usuario desmarca un ingrediente con `es_removible=true`
- **THEN** ese ingrediente se añade al array `excluidos` del CartItem

#### Scenario: Ingrediente no removible
- **WHEN** el sistema muestra ingredientes con `es_removible=false`
- **THEN** esos ingredientes están deshabilitados (no se pueden desmarcar)

### Requirement: Agregar producto al carrito
El sistema SHALL permitir al usuario agregar un producto al cartStore desde el catálogo o el detalle.

#### Scenario: Agregar desde catálogo
- **WHEN** el usuario hace clic en "Agregar" en una tarjeta
- **THEN** el producto se añade al cartStore con cantidad 1 y sin exclusiones

#### Scenario: Agregar desde detalle
- **WHEN** el usuario configura cantidad y exclusiones y hace clic en "Agregar al carrito"
- **THEN** el producto se añade al cartStore con la cantidad y exclusiones configuradas

#### Scenario: Producto ya en carrito
- **WHEN** el usuario agrega un producto que ya está en el carrito
- **THEN** la cantidad se incrementa (no se duplica el ítem), conforme a RN-CR03

### Requirement: CartDrawer lateral
El sistema SHALL mostrar un panel lateral deslizable con los ítems del carrito, controlado por `uiStore.cartOpen`.

#### Scenario: Abrir el carrito
- **WHEN** el usuario hace clic en el ícono de carrito en el header
- **THEN** el CartDrawer se abre mostrando los ítems actuales, el total y un botón "Ir al checkout"

#### Scenario: Carrito vacío en el drawer
- **WHEN** el CartDrawer se abre y el carrito no tiene ítems
- **THEN** muestra "Tu carrito está vacío" con link al catálogo

#### Scenario: Modificar cantidad en drawer
- **WHEN** el usuario cambia la cantidad de un ítem en el drawer
- **THEN** el cartStore actualiza la cantidad y el total se recalcula en tiempo real

#### Scenario: Eliminar ítem del drawer
- **WHEN** el usuario hace clic en "Eliminar" de un ítem
- **THEN** el ítem se remueve del cartStore y el drawer se actualiza

### Requirement: Página de inicio con acceso al catálogo
El sistema SHALL proveer una `HomePage` (`/`) funcional que dirija a los usuarios al catálogo.

#### Scenario: Usuario visita la raíz
- **WHEN** un usuario navega a `/`
- **THEN** el sistema muestra una página de bienvenida con hero y un CTA "Ver catálogo" que navega a `/productos`

### Requirement: Página de confirmación de pedido
El sistema SHALL proveer una `PedidoConfirmacionPage` (`/pedidos/:id`) que confirme el pedido creado.

#### Scenario: Pedido creado exitosamente
- **WHEN** el usuario llega a `/pedidos/:id` tras crear un pedido
- **THEN** el sistema muestra "¡Pedido creado!" con el ID del pedido, estado PENDIENTE y links a `/mis-pedidos` y `/productos`
