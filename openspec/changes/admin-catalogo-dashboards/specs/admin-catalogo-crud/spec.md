## ADDED Requirements

### Requirement: Dashboard CRUD de Categorías accesible para ADMIN y STOCK
El sistema SHALL proveer una página `/admin/categorias` que liste todas las categorías con paginación del lado del cliente. La página SHALL estar disponible para los roles ADMIN y STOCK. Cada fila SHALL mostrar: ID, nombre, descripción, estado activo/inactivo y acciones de editar y eliminar.

#### Scenario: ADMIN lista categorías
- **WHEN** un usuario con rol ADMIN navega a `/admin/categorias`
- **THEN** el sistema muestra una tabla con todas las categorías obtenidas del endpoint `GET /api/v1/categorias`

#### Scenario: STOCK lista categorías
- **WHEN** un usuario con rol STOCK navega a `/admin/categorias`
- **THEN** el sistema muestra la misma tabla de categorías con las mismas acciones

#### Scenario: Loading state en la tabla
- **WHEN** la query de categorías aún no completó
- **THEN** la tabla muestra un indicador de carga (skeleton o spinner) en lugar de filas vacías

#### Scenario: Estado de la tabla vacía
- **WHEN** no existen categorías en el sistema
- **THEN** la tabla muestra un mensaje "No hay categorías registradas"

### Requirement: Crear nueva categoría desde el admin panel
El sistema SHALL proveer un botón "Nueva Categoría" que abre un modal con formulario. El formulario SHALL requerir `nombre` (1-100 chars, patrón alfanumérico+acentos+guion+punto) y opcionalmente `descripcion` (máx 500 chars). Al confirmar SHALL llamar a `POST /api/v1/categorias` y, si tiene éxito, cerrar el modal e invalidar la lista.

#### Scenario: Crear categoría exitosamente
- **WHEN** el ADMIN completa el formulario con nombre válido y confirma
- **THEN** el sistema llama al endpoint de creación, cierra el modal, refresca la lista y muestra un toast de éxito

#### Scenario: Validación de nombre vacío
- **WHEN** el ADMIN intenta crear con nombre vacío
- **THEN** el sistema muestra un error de validación y no llama a la API

#### Scenario: Conflicto de nombre duplicado
- **WHEN** el backend devuelve HTTP 409
- **THEN** el sistema muestra el mensaje de error del backend en el formulario

### Requirement: Editar categoría existente desde el admin panel
El sistema SHALL proveer un botón de edición por fila que abre el mismo modal pre-cargado con los datos de la categoría seleccionada. Al confirmar SHALL llamar a `PUT /api/v1/categorias/{id}` y refrescar la lista.

#### Scenario: Editar nombre de una categoría
- **WHEN** el ADMIN hace clic en "Editar" de una fila y modifica el nombre
- **THEN** el sistema llama al endpoint de actualización con el nuevo nombre, cierra el modal y refresca la lista

#### Scenario: Modal pre-cargado con datos actuales
- **WHEN** el ADMIN abre el modal de edición
- **THEN** los campos muestran los valores actuales de la categoría (nombre y descripción)

### Requirement: Eliminar categoría con confirmación
El sistema SHALL proveer un botón de eliminación por fila. Al hacer clic SHALL mostrar un diálogo de confirmación con el nombre de la categoría. Si el usuario confirma SHALL llamar a `DELETE /api/v1/categorias/{id}` y refrescar la lista.

#### Scenario: Eliminar categoría con confirmación
- **WHEN** el ADMIN hace clic en "Eliminar" y confirma el diálogo
- **THEN** el sistema llama al endpoint de eliminación, refresca la lista y muestra un toast de éxito

#### Scenario: Cancelar eliminación
- **WHEN** el ADMIN hace clic en "Eliminar" pero cancela el diálogo
- **THEN** no se realiza ninguna llamada a la API y la lista permanece sin cambios

### Requirement: Dashboard CRUD de Ingredientes accesible para ADMIN y STOCK
El sistema SHALL proveer una página `/admin/ingredientes` que liste todos los ingredientes con paginación del lado del cliente. Cada fila SHALL mostrar: ID, nombre, unidad de medida, stock disponible, cantidad mínima, alerta de stock bajo (badge rojo si `alerta_stock_bajo=true`), estado activo/inactivo y acciones de editar y eliminar.

#### Scenario: ADMIN lista ingredientes con alerta de stock
- **WHEN** un ADMIN navega a `/admin/ingredientes`
- **THEN** los ingredientes con `alerta_stock_bajo=true` muestran un badge visual de alerta en la columna de stock

#### Scenario: Loading state en la tabla de ingredientes
- **WHEN** la query de ingredientes aún no completó
- **THEN** la tabla muestra un indicador de carga

### Requirement: Crear nuevo ingrediente desde el admin panel
El sistema SHALL proveer un botón "Nuevo Ingrediente" que abre un modal. El formulario SHALL requerir: `nombre`, `unidad_medida` (selector con opciones: gramos, litros, unidades, kilos, mililitros), `cantidad_stock` (≥0), `cantidad_minima` (≥0). Opcionalmente: `descripcion`, `categoria_id` (selector con categorías existentes). Al confirmar SHALL llamar a `POST /api/v1/ingredientes`.

#### Scenario: Crear ingrediente con todos los campos requeridos
- **WHEN** el ADMIN completa nombre, unidad de medida, cantidad_stock y cantidad_minima y confirma
- **THEN** el sistema llama al endpoint de creación, cierra el modal y refresca la lista

#### Scenario: Validación de cantidad negativa
- **WHEN** el ADMIN ingresa `cantidad_stock` o `cantidad_minima` negativo
- **THEN** el sistema muestra un error de validación y no llama a la API

### Requirement: Editar ingrediente existente desde el admin panel
El sistema SHALL permitir editar nombre, descripción, `cantidad_stock` y `cantidad_minima` de un ingrediente mediante `PUT /api/v1/ingredientes/{id}`. Los campos `unidad_medida` y `categoria_id` no son editables (el backend no los incluye en el schema de update).

#### Scenario: Editar stock de un ingrediente
- **WHEN** el ADMIN modifica `cantidad_stock` en el modal de edición y confirma
- **THEN** el sistema llama al endpoint con los nuevos valores y refresca la lista

### Requirement: Eliminar ingrediente con confirmación
El sistema SHALL proveer eliminación de ingredientes con el mismo patrón de confirmación que categorías, llamando a `DELETE /api/v1/ingredientes/{id}`.

#### Scenario: Eliminar ingrediente con confirmación
- **WHEN** el ADMIN confirma la eliminación de un ingrediente
- **THEN** el sistema llama al endpoint y refresca la lista

### Requirement: Dashboard CRUD de Productos accesible para ADMIN y STOCK
El sistema SHALL proveer una página `/admin/productos` que liste todos los productos. Cada fila SHALL mostrar: ID, nombre, precio base, categorías (badges), estado (`status`) y acciones de editar y eliminar.

#### Scenario: ADMIN lista productos
- **WHEN** un ADMIN navega a `/admin/productos`
- **THEN** el sistema muestra una tabla con todos los productos obtenidos de `GET /api/v1/productos`

### Requirement: Crear nuevo producto desde el admin panel
El sistema SHALL proveer un modal para crear productos. El formulario SHALL requerir: `nombre`, `base_price` (>0), al menos 1 `categoria` seleccionada (checkboxes sobre las categorías existentes), al menos 1 `ingrediente` con `quantity_required` >0 (tabla dinámica). Opcionalmente: `descripcion`. Al confirmar SHALL llamar a `POST /api/v1/productos`.

#### Scenario: Crear producto con categorías e ingredientes válidos
- **WHEN** el ADMIN completa todos los campos requeridos incluyendo al menos una categoría y un ingrediente con cantidad
- **THEN** el sistema llama al endpoint de creación con el body correcto y refresca la lista

#### Scenario: Validación de precio no positivo
- **WHEN** el ADMIN ingresa `base_price` igual o menor a 0
- **THEN** el sistema muestra error de validación y no llama a la API

#### Scenario: Validación de sin categorías seleccionadas
- **WHEN** el ADMIN intenta crear un producto sin seleccionar ninguna categoría
- **THEN** el sistema muestra un error de validación

#### Scenario: Validación de sin ingredientes con cantidad
- **WHEN** el ADMIN intenta crear un producto sin agregar ningún ingrediente
- **THEN** el sistema muestra un error de validación

### Requirement: Editar producto existente desde el admin panel
El sistema SHALL permitir editar nombre, precio, descripción, categorías e ingredientes de un producto mediante `PUT /api/v1/productos/{id}`, con el mismo modal pre-cargado con los datos actuales.

#### Scenario: Editar precio de un producto
- **WHEN** el ADMIN modifica `base_price` en el modal de edición y confirma
- **THEN** el sistema llama al endpoint de actualización y refresca la lista

### Requirement: Eliminar producto con confirmación
El sistema SHALL proveer eliminación de productos con el mismo patrón que las otras entidades, llamando a `DELETE /api/v1/productos/{id}`.

#### Scenario: Eliminar producto con confirmación
- **WHEN** el ADMIN confirma la eliminación de un producto
- **THEN** el sistema llama al endpoint y refresca la lista
