## ADDED Requirements

### Requirement: Listado de usuarios con búsqueda y paginación
El sistema SHALL exponer `GET /api/v1/admin/usuarios`, accesible solo para rol ADMIN, que devuelve el listado de usuarios. Acepta los parámetros de query `page` y `size` para paginación, un parámetro `q` para búsqueda por nombre o email, y filtros opcionales por `rol` y por `activo`. Cada usuario devuelto incluye sus datos básicos, sus roles y su estado `activo`. La respuesta nunca expone hashes de contraseña.

#### Scenario: ADMIN lista usuarios paginados
- **WHEN** un ADMIN hace `GET /api/v1/admin/usuarios?page=1&size=20`
- **THEN** el sistema responde HTTP 200 con la página de usuarios y los metadatos de paginación, sin exponer contraseñas

#### Scenario: Búsqueda por nombre o email
- **WHEN** un ADMIN hace `GET /api/v1/admin/usuarios?q=lucas`
- **THEN** el sistema responde HTTP 200 solo con usuarios cuyo nombre o email coincide con el término

#### Scenario: Filtro por rol y estado
- **WHEN** un ADMIN hace `GET /api/v1/admin/usuarios?rol=ADMIN&activo=true`
- **THEN** el sistema responde HTTP 200 solo con usuarios activos que tienen el rol ADMIN

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario sin rol ADMIN hace `GET /api/v1/admin/usuarios`
- **THEN** el sistema responde HTTP 403

### Requirement: Edición de datos y roles de un usuario
El sistema SHALL exponer un endpoint de actualización de usuario en `/api/v1/admin/usuarios/{id}`, accesible solo para rol ADMIN, que permite modificar los datos del usuario y el conjunto de roles asignados. Los roles asignados MUST existir en el catálogo de roles (ADMIN, STOCK, PEDIDOS, CLIENT). Cuando la operación modifica los roles del usuario, el sistema SHALL revocar todos los refresh tokens de ese usuario dentro de la misma transacción, forzando re-login con permisos actualizados. La operación SHALL rechazarse si dejaría al sistema sin ningún usuario con rol ADMIN (RN-RB04).

#### Scenario: ADMIN edita los datos de un usuario
- **WHEN** un ADMIN actualiza el nombre o email de un usuario existente
- **THEN** el sistema responde HTTP 200 con el usuario actualizado y persiste los cambios

#### Scenario: ADMIN cambia los roles de un usuario
- **WHEN** un ADMIN modifica el conjunto de roles de un usuario
- **THEN** el sistema persiste los nuevos roles y revoca todos los refresh tokens de ese usuario en la misma transacción

#### Scenario: Rol inexistente
- **WHEN** un ADMIN intenta asignar un rol que no existe en el catálogo
- **THEN** el sistema responde HTTP 422 y no aplica ningún cambio

#### Scenario: Operación dejaría al sistema sin ADMIN
- **WHEN** un ADMIN intenta quitar el rol ADMIN al último usuario que lo posee
- **THEN** el sistema responde HTTP 409 y no aplica el cambio

#### Scenario: Usuario inexistente
- **WHEN** un ADMIN intenta editar un usuario con un id inexistente
- **THEN** el sistema responde HTTP 404

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario sin rol ADMIN intenta editar un usuario
- **THEN** el sistema responde HTTP 403

### Requirement: Activación y desactivación de cuentas
El sistema SHALL exponer un endpoint para activar y desactivar cuentas de usuario en `/api/v1/admin/usuarios/{id}`, accesible solo para rol ADMIN, que modifica el campo `activo` del usuario. Al desactivar una cuenta, el sistema SHALL revocar todos los refresh tokens de ese usuario dentro de la misma transacción. El ADMIN NO puede desactivar su propia cuenta. La desactivación SHALL rechazarse si dejaría al sistema sin ningún usuario ADMIN activo (RN-RB04).

#### Scenario: ADMIN desactiva una cuenta
- **WHEN** un ADMIN desactiva la cuenta de otro usuario
- **THEN** el sistema marca `activo=false`, revoca todos los refresh tokens de ese usuario y responde HTTP 200

#### Scenario: ADMIN reactiva una cuenta
- **WHEN** un ADMIN activa una cuenta previamente desactivada
- **THEN** el sistema marca `activo=true` y responde HTTP 200

#### Scenario: ADMIN intenta auto-desactivarse
- **WHEN** un ADMIN intenta desactivar su propia cuenta
- **THEN** el sistema responde HTTP 409 y no aplica el cambio

#### Scenario: Desactivación dejaría al sistema sin ADMIN activo
- **WHEN** un ADMIN intenta desactivar al último ADMIN activo
- **THEN** el sistema responde HTTP 409 y no aplica el cambio

#### Scenario: Usuario sin rol ADMIN es rechazado
- **WHEN** un usuario sin rol ADMIN intenta activar o desactivar una cuenta
- **THEN** el sistema responde HTTP 403

### Requirement: Validación de cuenta activa en el login
El sistema SHALL rechazar el inicio de sesión de usuarios cuya cuenta está desactivada (`activo=false`). Cuando un usuario con credenciales válidas pero cuenta inactiva intenta autenticarse, el login SHALL responder HTTP 403 y no SHALL emitir tokens de acceso ni de refresh.

#### Scenario: Login de cuenta desactivada
- **WHEN** un usuario con credenciales correctas pero `activo=false` intenta iniciar sesión
- **THEN** el sistema responde HTTP 403 y no emite tokens

#### Scenario: Login de cuenta activa no se ve afectado
- **WHEN** un usuario con credenciales correctas y `activo=true` inicia sesión
- **THEN** el sistema responde HTTP 200 con el access token y el refresh token

#### Scenario: Cuenta reactivada puede volver a iniciar sesión
- **WHEN** un usuario previamente desactivado y luego reactivado inicia sesión con credenciales correctas
- **THEN** el sistema responde HTTP 200 con los tokens
