## Why

El sistema Food Store requiere autenticación segura y control de acceso basado en roles para proteger datos de usuarios, productos y pedidos. Sin autenticación, cualquiera puede acceder a operaciones administrativas (crear productos, ver pedidos ajenos, etc.). Necesitamos un mecanismo robusto de login/registro con cifrado de contraseñas, tokens JWT y validación de roles (admin vs customer) antes de habilitar cualquier funcionalidad operativa.

## What Changes

- **Nuevo modelo Usuario** con email, contraseña cifrada (bcrypt), rol (admin | customer), estado activo/inactivo
- **Endpoints de autenticación**: `/auth/register`, `/auth/login`, `/auth/me`, `/auth/logout`
- **Token JWT (HS256)** con access_token (corta vida) + refresh_token (larga vida)
- **Rate limiting** en login: máx 5 intentos cada 15 minutos por IP (slowapi)
- **Middleware de verificación JWT** para proteger endpoints privados
- **Decoradores @require_role()** para validar permisos (admin-only, customer-only)
- **Servicio de hashing** con Passlib + bcrypt
- **Repository de Usuario** integrado con Unit of Work existente
- Actualización de `.env` con `SECRET_KEY`, `JWT_ALGORITHM`, duraciones de tokens

## Capabilities

### New Capabilities

- `user-auth`: Registro, login, gestión de sesiones JWT con access + refresh tokens
- `user-roles`: Control de acceso basado en roles (admin, customer) con decoradores
- `password-security`: Hashing con bcrypt, validación de complejidad
- `rate-limiting`: Protección contra ataques de fuerza bruta en endpoints sensibles

### Modified Capabilities

- `user-model`: El modelo Usuario se expande con email, password_hash, role, status (no sólo id + nombre)

## Impact

- **Dependencies**: Passlib, slowapi, python-jose, FastAPI (a confirmar versión)
- **Backend folders**: Nuevas carpetas `/backend`, `/routers/auth`, `/schemas`, `/services/auth`, `/middleware`
- **Database schema**: Tabla `usuarios` con columnas: id, email (unique), password_hash, role, created_at, updated_at
- **Environment**: `.env` debe tener `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`
- **Breaking changes**: Ninguna (es feature nueva)
- **Downstream**: auth-roles es dependencia de todos los CRUDs posteriores (categoria-crud, producto-crud, cliente-crud, etc.)
