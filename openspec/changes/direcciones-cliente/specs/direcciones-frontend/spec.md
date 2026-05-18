# direcciones-frontend Specification

## Purpose

Define el comportamiento de la capa frontend para que un cliente autenticado gestione
sus direcciones de entrega (CRUD + predeterminada) y seleccione una dirección durante
el checkout. El backend ya provee los endpoints (`direcciones-gestion`,
`direcciones-predeterminada`); este capability cubre únicamente la UI y la capa de
estado de servidor del frontend.

## ADDED Requirements

### Requirement: Hooks centralizados de direcciones

El frontend SHALL exponer la capa de estado de servidor de direcciones a través de
hooks TanStack Query en `features/pedidos/hooks/useDirecciones.ts`. Los componentes
SHALL NOT declarar `useQuery` ni `useMutation` de direcciones inline. Todos los hooks
SHALL compartir una única `queryKey` `['direcciones']`.

#### Scenario: Listado de direcciones

- **WHEN** un componente invoca `useDirecciones()`
- **THEN** el hook devuelve las direcciones activas del cliente autenticado mediante
  `GET /api/v1/clientes/me/direcciones`, expuestas como estado de servidor cacheado

#### Scenario: Invalidación de caché tras una mutación

- **WHEN** una mutación de crear, actualizar, eliminar o marcar predeterminada finaliza
  con éxito
- **THEN** el hook invalida la `queryKey` `['direcciones']` y la lista se vuelve a
  obtener, reflejando el estado actualizado

### Requirement: Gestión CRUD de direcciones desde la UI

El cliente autenticado SHALL poder listar, crear, editar y eliminar (baja lógica) sus
direcciones de entrega, y marcar una como predeterminada, desde una interfaz
alcanzable mediante navegación.

#### Scenario: Listar direcciones en el perfil

- **WHEN** el cliente abre su perfil o la página `/perfil/direcciones`
- **THEN** la UI muestra la lista de sus direcciones activas, identificando claramente
  cuál es la predeterminada

#### Scenario: Crear una dirección

- **WHEN** el cliente completa el formulario con calle, número, ciudad, provincia y
  código postal y confirma
- **THEN** la dirección se crea vía `POST /api/v1/clientes/me/direcciones` y aparece en
  la lista sin recargar la página

#### Scenario: Editar una dirección

- **WHEN** el cliente edita los campos de una dirección existente y confirma
- **THEN** la dirección se actualiza vía `PUT /api/v1/clientes/me/direcciones/{id}` y
  la lista refleja los nuevos valores

#### Scenario: Eliminar una dirección

- **WHEN** el cliente elimina una dirección
- **THEN** la dirección se da de baja lógica vía `DELETE /api/v1/clientes/me/direcciones/{id}`
  y deja de aparecer en la lista

#### Scenario: Marcar dirección como predeterminada

- **WHEN** el cliente marca una dirección no predeterminada como predeterminada
- **THEN** se invoca `PUT /api/v1/clientes/me/direcciones/{id}/predeterminada`, esa
  dirección queda señalada como predeterminada y las demás dejan de estarlo (RN-DI02)

#### Scenario: Cliente sin direcciones

- **WHEN** el cliente no tiene ninguna dirección registrada
- **THEN** la UI muestra un mensaje indicando que debe agregar una dirección para
  poder realizar pedidos

### Requirement: Ruta dedicada de gestión de direcciones

El frontend SHALL exponer la ruta protegida `/perfil/direcciones`, accesible solo para
usuarios autenticados, que renderiza la interfaz de gestión CRUD de direcciones.

#### Scenario: Acceso autenticado a la ruta de direcciones

- **WHEN** un cliente autenticado navega a `/perfil/direcciones`
- **THEN** se muestra la página de gestión de direcciones dentro del layout principal

#### Scenario: Acceso sin autenticación

- **WHEN** un usuario no autenticado intenta acceder a `/perfil/direcciones`
- **THEN** es redirigido a `/login`

### Requirement: Selección de dirección en el checkout

Durante el checkout el cliente SHALL seleccionar una dirección de entrega entre sus
direcciones guardadas antes de poder crear el pedido.

#### Scenario: Pre-selección de la dirección predeterminada

- **WHEN** el cliente abre el checkout y tiene al menos una dirección guardada
- **THEN** el selector de direcciones pre-selecciona la dirección predeterminada (o la
  primera si no hay predeterminada)

#### Scenario: Checkout sin direcciones

- **WHEN** el cliente abre el checkout y no tiene ninguna dirección guardada
- **THEN** el selector muestra un mensaje y un enlace a `/perfil/direcciones` para crear
  una, y no se permite continuar con la creación del pedido

#### Scenario: Continuación bloqueada sin dirección seleccionada

- **WHEN** no hay ninguna dirección seleccionada en el checkout
- **THEN** la acción de crear el pedido permanece deshabilitada hasta que se seleccione
  una dirección
