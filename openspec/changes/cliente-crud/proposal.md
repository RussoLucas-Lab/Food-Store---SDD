## Why

Food Store necesita gestionar clientes del sistema: registrar nuevos clientes, permitirles editar su información personal y administrativos borrar clientes cuando sea necesario. Los clientes son entidades centrales para crear pedidos (carrito-pedidos depende directamente de esto). Sin CRUD de clientes, no podemos avanzar en la lógica de compra y pago.

## What Changes

- **Backend API**: Nuevos endpoints para registrar, listar, obtener, editar y borrar clientes (CRUD REST).
- **Modelos Cliente**: Tabla con campos típicos (id, nombre, email, teléfono, dirección, etc.).
- **Validaciones**: Validar email único, campos requeridos, formato de teléfono, etc.
- **Autenticación**: Solo usuarios autenticados pueden operar; roles específicos pueden ver/editar/borrar clientes.
- **Soft Delete**: Los clientes borrados son marcados como inactivos, nunca se eliminan de la BD.
- **Frontend**: Páginas para listar, crear, editar y borrar clientes (UI basic, sin estilos avanzados aún).

## Capabilities

### New Capabilities
- `cliente-registro`: Permitir crear nuevos clientes con validación de datos únicos (email) y requeridos.
- `cliente-edicion`: Permitir que clientes editen su perfil o que admins editen cualquier cliente.
- `cliente-listado`: Listar todos los clientes activos con filtrado y búsqueda.
- `cliente-borrado`: Marcar clientes como inactivos (soft delete), solo accesible por admins.
- `cliente-validaciones`: Reglas de validación de datos de cliente (email, teléfono, dirección).

### Modified Capabilities
- `autenticacion`: Los endpoints de cliente requieren autenticación y validación de roles (admin puede ver todos, usuario normal solo su propio perfil).

## Impact

- **Backend**: Nuevos modelos, repositorio, service layer, schemas Pydantic, endpoints REST.
- **Database**: Nueva tabla `clientes` con índices en email y activo.
- **Frontend**: Nuevas rutas `/clientes`, `/clientes/:id/editar`, componentes de CRUD.
- **Auth**: Refuerzo de control de acceso por roles (ya existe, extendemos reglas).
- **Dependencias**: Nada nuevo; usa stack existente (FastAPI, SQLAlchemy, React, etc.).
